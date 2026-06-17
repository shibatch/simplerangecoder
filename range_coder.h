#ifndef RANGE_CODER_H
#define RANGE_CODER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Range Encode Interface
 *
 * @param q_vals Input array of signed integers.
 * @param num_vals Number of elements in q_vals.
 * @param cum_freqs Cumulative frequency array (size: alphabet_size + 1).
 * @param freqs Individual frequency array (size: alphabet_size).
 * @param alphabet_size Maximum number of buckets.
 * @param tot_freq Sum of frequencies (must match cum_freqs[alphabet_size]).
 * @param sym_shift Offset to convert q_val to positive index (sym = q_val + sym_shift).
 * @param out_buf Output buffer for compressed byte stream.
 * @param out_buf_len Maximum size of out_buf.
 * @return int32_t Number of bytes written, or -1 on error (e.g., buffer overflow).
 */
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
);

/**
 * @brief Range Decode Interface
 *
 * @param data Compressed byte stream.
 * @param data_len Length of data in bytes.
 * @param block_len Number of elements to reconstruct.
 * @param cum_freqs Cumulative frequency array.
 * @param freqs Individual frequency array.
 * @param alphabet_size Maximum number of buckets.
 * @param tot_freq Sum of frequencies.
 * @param sym_shift Offset used during encoding.
 * @param out_q_vals Output array for reconstructed integers.
 * @return int32_t 0 on success, or negative error code.
 */
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
);

/**
 * @brief Batch Range Encode using OpenMP
 *
 * @param num_blocks Number of blocks to encode.
 * @param all_q_vals Flat array of symbols.
 * @param block_size Number of symbols per block.
 * @param lut_cum_freqs Flat LUT of cumulative frequencies.
 * @param lut_freqs Flat LUT of frequencies.
 * @param max_alphabet_size Stride for LUT indexing.
 * @param all_decay_indices Indices into LUT for each block.
 * @param all_alphabet_sizes Alphabet sizes for each block.
 * @param all_tot_freqs Total frequencies for each block.
 * @param all_sym_shifts Symbol shifts for each block.
 * @param all_output_buffers Flat pre-allocated output buffer.
 * @param max_output_size_per_block Reserved size per block in all_output_buffers.
 * @param all_output_sizes Array to store actual written size for each block (or -1 on error).
 */
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
);

/**
 * @brief Batch Range Decode using OpenMP
 *
 * @param num_blocks Number of blocks to decode.
 * @param all_compressed_data Flat array of compressed data.
 * @param max_output_size_per_block Stride for compressed data input.
 * @param all_compressed_lengths Actual length of each compressed block.
 * @param block_size Number of symbols per block.
 * @param lut_cum_freqs Flat LUT of cumulative frequencies.
 * @param lut_freqs Flat LUT of frequencies.
 * @param max_alphabet_size Stride for LUT indexing.
 * @param all_decay_indices Indices into LUT for each block.
 * @param all_alphabet_sizes Alphabet sizes for each block.
 * @param all_tot_freqs Total frequencies for each block.
 * @param all_sym_shifts Symbol shifts for each block.
 * @param all_out_q_vals Flat array to store reconstructed integers.
 * @param all_ret_codes Array to store return codes (0 on success, negative on error).
 */
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
);

/**
 * @brief rANS Encode Interface
 */
int32_t ans_encode_interface(
    const int32_t* q_vals,
    int32_t num_vals,
    const int32_t* cum_freqs,
    const int32_t* freqs,
    int32_t alphabet_size,
    int32_t tot_freq,
    int32_t sym_shift,
    uint8_t* out_buf,
    int32_t out_buf_len
);

/**
 * @brief rANS Decode Interface
 */
int32_t ans_decode_interface(
    const uint8_t* data,
    int32_t data_len,
    int32_t block_len,
    const int32_t* cum_freqs,
    const int32_t* freqs,
    int32_t alphabet_size,
    int32_t tot_freq,
    int32_t sym_shift,
    int32_t* out_q_vals
);

/**
 * @brief Batch rANS Encode using OpenMP
 */
void ans_encode_batch(
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
);

/**
 * @brief Batch rANS Decode using OpenMP
 */
void ans_decode_batch(
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
);

#ifdef __cplusplus
}
#endif

#endif // RANGE_CODER_H
