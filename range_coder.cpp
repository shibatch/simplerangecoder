#include "range_coder.h"
#include <stdint.h>
#include <omp.h>

extern "C" {

int32_t range_encode_interface(
    const int32_t* q_vals,
    int32_t num_vals,
    const int32_t* cum_freqs,
    const int32_t* freqs,
    int32_t alphabet_size,
    int32_t tot_freq,
    int32_t sym_shift,
    uint8_t* out_buf,
    int32_t out_buf_len
) {
    if (!q_vals || !cum_freqs || !freqs || !out_buf || num_vals < 0 || alphabet_size <= 0 || tot_freq <= 0) {
        return -1;
    }

    uint64_t low = 0;
    uint32_t range = 0xFFFFFFFF;
    int32_t out_pos = 0;

    uint8_t cache = 0;
    uint64_t cache_size = 0;

    auto shift_low = [&]() -> bool {
        if (low < 0xFF000000ULL || low >= 0x100000000ULL) {
            if (out_pos < out_buf_len) {
                out_buf[out_pos++] = cache + (uint8_t)(low >> 32);
            } else return false;

            uint8_t carry_byte = (low >> 32) ? 0x00 : 0xFF;
            for (; cache_size > 0; cache_size--) {
                if (out_pos < out_buf_len) {
                    out_buf[out_pos++] = carry_byte;
                } else return false;
            }
            cache = (uint8_t)(low >> 24);
        } else {
            cache_size++;
        }
        low = (uint64_t)((uint32_t)low << 8);
        return true;
    };

    for (int32_t i = 0; i < num_vals; ++i) {
        int32_t sym = q_vals[i] + sym_shift;
        if (sym < 0) {
            sym = 0;
        } else if (sym >= alphabet_size) {
            sym = alphabet_size - 1;
        }

        uint32_t r = range / tot_freq;
        low += (uint64_t)cum_freqs[sym] * r;
        range = (uint32_t)freqs[sym] * r;

        while (range < 0x01000000) {
            range <<= 8;
            if (!shift_low()) return -1;
        }
    }

    for (int i = 0; i < 5; ++i) {
        if (!shift_low()) return -1;
    }

    return out_pos;
}

int32_t range_decode_interface(
    const uint8_t* data,
    int32_t data_len,
    int32_t block_len,
    const int32_t* cum_freqs,
    const int32_t* freqs,
    int32_t alphabet_size,
    int32_t tot_freq,
    int32_t sym_shift,
    int32_t* out_q_vals
) {
    if (!out_q_vals || block_len < 0) return -1;
    if (data_len <= 0) {
        for (int32_t i = 0; i < block_len; ++i) {
            out_q_vals[i] = 0;
        }
        return 0;
    }
    if (!data || !cum_freqs || !freqs || alphabet_size <= 0 || tot_freq <= 0) {
        return -1;
    }

    uint32_t range = 0xFFFFFFFF;
    uint32_t code = 0;
    int32_t data_pos = 0;

    auto get_byte = [&]() -> uint8_t {
        if (data_pos < data_len) return data[data_pos++];
        return 0;
    };

    for (int i = 0; i < 5; ++i) {
        code = (code << 8) | get_byte();
    }

    for (int32_t i = 0; i < block_len; ++i) {
        uint32_t r = range / tot_freq;
        if (r == 0) return -2; // Should not happen if tot_freq < 0x01000000
        uint32_t count = code / r;

        if (count >= (uint32_t)tot_freq) return -2;

        int32_t sym = 0;
        int32_t start = 0, end = alphabet_size - 1;
        while (start <= end) {
            int32_t mid = start + (end - start) / 2;
            if ((uint32_t)cum_freqs[mid] <= count) {
                sym = mid;
                start = mid + 1;
            } else {
                end = mid - 1;
            }
        }

        if (count < (uint32_t)cum_freqs[sym] || count >= (uint32_t)cum_freqs[sym+1]) {
            return -2;
        }

        out_q_vals[i] = sym - sym_shift;

        code -= (uint32_t)cum_freqs[sym] * r;
        range = (uint32_t)freqs[sym] * r;

        while (range < 0x01000000) {
            range <<= 8;
            code = (code << 8) | get_byte();
        }
    }

    return 0;
}

void range_encode_batch(
    int32_t num_blocks,
    const int32_t* all_q_vals,
    int32_t block_size,
    const int32_t* lut_cum_freqs,
    const int32_t* lut_freqs,
    int32_t max_alphabet_size,
    const int32_t* all_decay_indices,
    const int32_t* all_alphabet_sizes,
    const int32_t* all_tot_freqs,
    const int32_t* all_sym_shifts,
    uint8_t* all_output_buffers,
    int32_t max_output_size_per_block,
    int32_t* all_output_sizes
) {
    #pragma omp parallel for
    for (int32_t i = 0; i < num_blocks; ++i) {
        int32_t decay_idx = all_decay_indices[i];
        const int32_t* cum_freqs = lut_cum_freqs + (decay_idx * (max_alphabet_size + 1));
        const int32_t* freqs = lut_freqs + (decay_idx * max_alphabet_size);

        all_output_sizes[i] = range_encode_interface(
            all_q_vals + (i * (int64_t)block_size),
            block_size,
            cum_freqs,
            freqs,
            all_alphabet_sizes[i],
            all_tot_freqs[i],
            all_sym_shifts[i],
            all_output_buffers + (i * (int64_t)max_output_size_per_block),
            max_output_size_per_block
        );
    }
}

void range_decode_batch(
    int32_t num_blocks,
    const uint8_t* all_compressed_data,
    int32_t max_output_size_per_block,
    const int32_t* all_compressed_lengths,
    int32_t block_size,
    const int32_t* lut_cum_freqs,
    const int32_t* lut_freqs,
    int32_t max_alphabet_size,
    const int32_t* all_decay_indices,
    const int32_t* all_alphabet_sizes,
    const int32_t* all_tot_freqs,
    const int32_t* all_sym_shifts,
    int32_t* all_out_q_vals,
    int32_t* all_ret_codes
) {
    #pragma omp parallel for
    for (int32_t i = 0; i < num_blocks; ++i) {
        int32_t decay_idx = all_decay_indices[i];
        const int32_t* cum_freqs = lut_cum_freqs + (decay_idx * (max_alphabet_size + 1));
        const int32_t* freqs = lut_freqs + (decay_idx * max_alphabet_size);

        all_ret_codes[i] = range_decode_interface(
            all_compressed_data + (i * (int64_t)max_output_size_per_block),
            all_compressed_lengths[i],
            block_size,
            cum_freqs,
            freqs,
            all_alphabet_sizes[i],
            all_tot_freqs[i],
            all_sym_shifts[i],
            all_out_q_vals + (i * (int64_t)block_size)
        );
    }
}

}
