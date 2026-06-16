#include "range_coder.h"
#include <iostream>
#include <vector>

int main() {
    std::cout << "Range Coder C++ Hello World" << std::endl;

    const int32_t alphabet_size = 257;
    const int32_t tot_freq = 1028;
    const int32_t sym_shift = 0;

    std::vector<int32_t> freqs(alphabet_size, 4);
    std::vector<int32_t> cum_freqs(alphabet_size + 1, 0);
    for(int i=0; i<alphabet_size; ++i) cum_freqs[i+1] = cum_freqs[i] + freqs[i];

    std::vector<int32_t> input = {10, 20, 30, 40, 50};
    std::vector<uint8_t> buffer(1024);

    int32_t size = range_encode_interface(
        input.data(), input.size(), cum_freqs.data(), freqs.data(),
        alphabet_size, tot_freq, sym_shift, buffer.data(), buffer.size()
    );

    std::cout << "Encoded " << input.size() << " values into " << size << " bytes." << std::endl;

    std::vector<int32_t> output(input.size());
    range_decode_interface(
        buffer.data(), size, output.size(), cum_freqs.data(), freqs.data(),
        alphabet_size, tot_freq, sym_shift, output.data()
    );

    std::cout << "Decoded values: ";
    for(auto v : output) std::cout << v << " ";
    std::cout << std::endl;

    return 0;
}
