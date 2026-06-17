#include "range_coder.h"
#include <iostream>
#include <vector>
#include <numeric>
#include <cassert>

int main() {
    const int num_blocks = 2;
    const int block_size = 5;
    const int alphabet_size = 256;
    const int max_alphabet_size = alphabet_size;
    const int tot_freq = 65536; // Strict requirement for rANS

    // 1. Prepare frequency tables (Example: Uniform distribution)
    std::vector<int32_t> lut_freqs(num_blocks * max_alphabet_size, tot_freq / alphabet_size);
    std::vector<int32_t> lut_cum_freqs(num_blocks * (max_alphabet_size + 1), 0);
    for (int b = 0; b < num_blocks; ++b) {
        int32_t* f = &lut_freqs[b * max_alphabet_size];
        int32_t* cf = &lut_cum_freqs[b * (max_alphabet_size + 1)];
        for (int i = 0; i < alphabet_size; ++i) {
            cf[i+1] = cf[i] + f[i];
        }
        // Ensure the last cum_freq matches tot_freq
        cf[alphabet_size] = tot_freq;
    }

    // 2. Input data
    std::vector<int32_t> all_q_vals = {
        10, 20, 30, 40, 50,  // Block 0
        5, 15, 25, 35, 45    // Block 1
    };

    // 3. Metadata for batch processing
    std::vector<int32_t> all_decay_indices = {0, 1};
    std::vector<int32_t> all_alphabet_sizes = {alphabet_size, alphabet_size};
    std::vector<int32_t> all_tot_freqs = {tot_freq, tot_freq}; // MUST be 65536
    std::vector<int32_t> all_sym_shifts = {0, 0};

    // 4. Output buffers
    int max_output_size_per_block = block_size * 4 + 64;
    std::vector<uint8_t> all_output_buffers(num_blocks * max_output_size_per_block);
    std::vector<int32_t> all_output_sizes(num_blocks);

    // 5. Batch Encode
    ans_encode_batch(
        num_blocks,
        all_q_vals.data(),
        block_size,
        lut_cum_freqs.data(),
        lut_freqs.data(),
        max_alphabet_size,
        all_decay_indices.data(),
        all_alphabet_sizes.data(),
        all_tot_freqs.data(),
        all_sym_shifts.data(),
        all_output_buffers.data(),
        max_output_size_per_block,
        all_output_sizes.data()
    );

    std::cout << "Batch Encode completed." << std::endl;
    for (int i = 0; i < num_blocks; ++i) {
        std::cout << "Block " << i << " size: " << all_output_sizes[i] << " bytes" << std::endl;
    }

    // 6. Batch Decode
    std::vector<int32_t> all_out_q_vals(num_blocks * block_size);
    std::vector<int32_t> all_ret_codes(num_blocks);

    ans_decode_batch(
        num_blocks,
        all_output_buffers.data(),
        max_output_size_per_block,
        all_output_sizes.data(),
        block_size,
        lut_cum_freqs.data(),
        lut_freqs.data(),
        max_alphabet_size,
        all_decay_indices.data(),
        all_alphabet_sizes.data(),
        all_tot_freqs.data(),
        all_sym_shifts.data(),
        all_out_q_vals.data(),
        all_ret_codes.data()
    );

    // 7. Verify
    for (int i = 0; i < (int)all_q_vals.size(); ++i) {
        assert(all_q_vals[i] == all_out_q_vals[i]);
    }

    std::cout << "Batch Decode verified successfully!" << std::endl;

    return 0;
}
