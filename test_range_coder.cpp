#include "range_coder.h"
#include <iostream>
#include <vector>
#include <random>
#include <cassert>
#include <numeric>

void run_test(int32_t num_vals) {
    std::cout << "Testing with " << num_vals << " values..." << std::endl;

    const int32_t alphabet_size = 257;
    const int32_t freq_val = 4;
    const int32_t tot_freq = alphabet_size * freq_val;
    const int32_t sym_shift = 0;

    std::vector<int32_t> freqs(alphabet_size, freq_val);
    std::vector<int32_t> cum_freqs(alphabet_size + 1);
    cum_freqs[0] = 0;
    for (int i = 0; i < alphabet_size; ++i) {
        cum_freqs[i+1] = cum_freqs[i] + freqs[i];
    }

    std::vector<int32_t> q_vals(num_vals);
    std::mt19937 gen(42);
    std::uniform_int_distribution<> dis(0, alphabet_size - 1);
    for (int i = 0; i < num_vals; ++i) {
        q_vals[i] = dis(gen);
    }

    std::vector<uint8_t> out_buf(num_vals * 4 + 64);
    int32_t encoded_size = range_encode_interface(
        q_vals.data(), num_vals, cum_freqs.data(), freqs.data(),
        alphabet_size, tot_freq, sym_shift, out_buf.data(), out_buf.size()
    );

    assert(encoded_size > 0);
    std::cout << "Encoded size: " << encoded_size << " bytes" << std::endl;

    std::vector<int32_t> decoded_q_vals(num_vals);
    int32_t ret = range_decode_interface(
        out_buf.data(), encoded_size, num_vals, cum_freqs.data(), freqs.data(),
        alphabet_size, tot_freq, sym_shift, decoded_q_vals.data()
    );

    assert(ret == 0);

    for (int i = 0; i < num_vals; ++i) {
        if (q_vals[i] != decoded_q_vals[i]) {
            std::cerr << "Mismatch at index " << i << ": expected " << q_vals[i]
                      << ", got " << decoded_q_vals[i] << std::endl;
            exit(1);
        }
    }
    std::cout << "Test passed!" << std::endl;
}

int main() {
    run_test(4);
    run_test(4096);
    run_test(16384);
    std::cout << "All C++ tests passed!" << std::endl;
    return 0;
}
