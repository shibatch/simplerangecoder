# Simple Range Coder

A simple range coding library implemented in C++20 with a Python wrapper. While simple, it provides better performance than a pure Python implementation. This component provides entropy encoding and decoding for signed integer arrays.

## License

This project is licensed under [CC0 1.0 Universal](LICENSE).

## Features

- **Algorithms**:
  - Schindler's 32-bit top-down Range Coder.
  - rANS (Range Asymmetric Numeral Systems) with LIFO concealment (reverse encoding).
- **Precision**: 32-bit state for both algorithms.
- **Parallelization**: OpenMP-accelerated batch encoding and decoding for both backends.
- **Interfaces**: C-ABI (C++20) and Python (via `ctypes`).
- **Safety**: Buffer overflow protection and stream consistency checks.

## Component Structure

- `range_coder.h` / `range_coder.cpp`: C++ core logic.
- `fast_rc.py`: Python wrapper (`SimpleRangeCoder` class).
- `Makefile`: Build automation.
- `hello_world.cpp` / `hello_world.py`: Usage examples.

## Requirements

- GCC 9+ or Clang (supporting C++20)
- Python 3.7+
- NumPy

## Build and Test

To build the shared library and testers:

```bash
make all
```

To run both C++ and Python tests:

```bash
make test
```

To run hello world examples:

```bash
make hello
```

## API Documentation

### C++ ABI (`extern "C"`)

The library provides two entropy coding backends: Range Coder and rANS. Both follow the same C-ABI for easy interchangeability.

#### `range_encode_interface` / `ans_encode_interface`
Encodes an array of integers into a byte stream.
**Note**: For `ans_encode_interface`, `tot_freq` must be `65536`.

```cpp
int32_t range_encode_interface( // or ans_encode_interface
    const int32_t* q_vals,    // Input integers
    int32_t num_vals,         // Number of input integers
    const int32_t* cum_freqs, // Cumulative frequencies (alphabet_size + 1)
    const int32_t* freqs,     // Individual frequencies (alphabet_size)
    int32_t alphabet_size,    // Number of possible symbols
    int32_t tot_freq,         // Sum of frequencies (Must be 65536 for rANS)
    int32_t sym_shift,        // Offset: sym = q_val + sym_shift
    uint8_t* out_buf,         // Output buffer
    int32_t out_buf_len       // Output buffer capacity
);
```
**Returns**: Number of bytes written, or `-1` on failure (e.g., buffer overflow).

#### `range_decode_interface` / `ans_decode_interface`
Decodes a byte stream back into integers.
**Note**: For `ans_decode_interface`, `tot_freq` must be `65536`.

```cpp
int32_t range_decode_interface( // or ans_decode_interface
    const uint8_t* data,      // Compressed byte stream
    int32_t data_len,         // Length of input data
    int32_t block_len,        // Number of elements to decode
    const int32_t* cum_freqs, // Cumulative frequencies
    const int32_t* freqs,     // Individual frequencies
    int32_t alphabet_size,    // Number of symbols
    int32_t tot_freq,         // Sum of frequencies (Must be 65536 for rANS)
    int32_t sym_shift,        // Same offset as used in encoding
    int32_t* out_q_vals       // Output array for integers
);
```
**Returns**: `0` on success, negative error code on failure.

#### `range_encode_batch` / `ans_encode_batch`
Encodes multiple blocks in parallel using OpenMP. The argument structure is identical for both Range Coder and rANS backends.
**Note**: For rANS, `all_tot_freqs` must contain `65536` for all blocks.

```cpp
void range_encode_batch( // or ans_encode_batch
    int32_t num_blocks,               // Total number of blocks to process
    const int32_t* all_q_vals,        // Flat array of input symbols [num_blocks * block_size]
    int32_t block_size,               // Number of symbols per block
    const int32_t* lut_cum_freqs,     // Flat LUT of cumulative frequencies
    const int32_t* lut_freqs,         // Flat LUT of frequencies
    int32_t max_alphabet_size,        // Stride for LUT indexing
    const int32_t* all_decay_indices, // Indices into LUT for each block
    const int32_t* all_alphabet_sizes,// Alphabet sizes for each block
    const int32_t* all_tot_freqs,     // Total frequencies for each block (Must be 65536 for rANS)
    const int32_t* all_sym_shifts,    // Symbol shifts for each block
    uint8_t* all_output_buffers,      // Flat pre-allocated output buffer [num_blocks * max_output_size_per_block]
    int32_t max_output_size_per_block,// Reserved size per block in all_output_buffers
    int32_t* all_output_sizes         // Array to store actual written size for each block (or -1 on error)
);
```

#### `range_decode_batch` / `ans_decode_batch`
Decodes multiple blocks in parallel using OpenMP.
**Note**: For rANS, `all_tot_freqs` must contain `65536` for all blocks.

```cpp
void range_decode_batch( // or ans_decode_batch
    int32_t num_blocks,               // Number of blocks to decode
    const uint8_t* all_compressed_data, // Flat array of compressed data [num_blocks * max_output_size_per_block]
    int32_t max_output_size_per_block,// Stride for compressed data input
    const int32_t* all_compressed_lengths, // Actual length of each compressed block
    int32_t block_size,               // Number of symbols per block
    const int32_t* lut_cum_freqs,     // Flat LUT of cumulative frequencies
    const int32_t* lut_freqs,         // Flat LUT of frequencies
    int32_t max_alphabet_size,        // Stride for LUT indexing
    const int32_t* all_decay_indices, // Indices into LUT for each block
    const int32_t* all_alphabet_sizes,// Alphabet sizes for each block
    const int32_t* all_tot_freqs,     // Total frequencies for each block (Must be 65536 for rANS)
    const int32_t* all_sym_shifts,    // Symbol shifts for each block
    int32_t* all_out_q_vals,          // Flat array to store reconstructed integers [num_blocks * block_size]
    int32_t* all_ret_codes            // Array to store return codes (0 on success, negative on error)
);
```


### Python API (`SimpleRangeCoder`)

The Python API provides methods for both Range Coding and rANS. The argument structures are consistent across both backends.

#### Range Coder Methods
- `encode(q_vals, cum_freqs, freqs, tot_freq, sym_shift)`: Encodes a single array of integers.
- `decode(data_bytes, block_len, cum_freqs, freqs, tot_freq, sym_shift)`: Decodes a byte stream.
- `batch_encode(all_q_vals, lut_cum_freqs, lut_freqs, max_alphabet_size, all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts)`: Encodes multiple blocks in parallel.
- `batch_decode(all_compressed_data, all_compressed_lengths, block_size, lut_cum_freqs, lut_freqs, max_alphabet_size, all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts)`: Decodes multiple blocks in parallel.

#### rANS Methods
**Note**: For all rANS methods, `tot_freq` (or values in `all_tot_freqs`) must be `65536`.

- `ans_encode(q_vals, cum_freqs, freqs, tot_freq, sym_shift)`: rANS version of `encode`.
- `ans_decode(data_bytes, block_len, cum_freqs, freqs, tot_freq, sym_shift)`: rANS version of `decode`.
- `batch_ans_encode(all_q_vals, lut_cum_freqs, lut_freqs, max_alphabet_size, all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts)`: rANS version of `batch_encode`.
- `batch_ans_decode(all_compressed_data, all_compressed_lengths, block_size, lut_cum_freqs, lut_freqs, max_alphabet_size, all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts)`: rANS version of `batch_decode`.

## Python Integration

To use this library in your Python project:

1.  **Build the shared library**: Run `make librangecoder.so` to generate the `.so` file.
2.  **Library Placement**:
    - By default, `SimpleRangeCoder` looks for `./librangecoder.so` in the current working directory.
    - You can place the `.so` file anywhere and provide the path to the constructor:
      ```python
      rc = SimpleRangeCoder("/path/to/librangecoder.so")
      ```
3.  **Dependencies**: Ensure `numpy` is installed in your Python environment.

## Usage Example (Python)

```python
import numpy as np
from fast_rc import SimpleRangeCoder

# Initialize with the path to the shared library
rc = SimpleRangeCoder("./librangecoder.so")

# Prepare probability model (Example: Uniform distribution)
alphabet_size = 257
freqs = np.full(alphabet_size, 4, dtype=np.int32)
cum_freqs = np.zeros(alphabet_size + 1, dtype=np.int32)
cum_freqs[1:] = np.cumsum(freqs)
tot_freq = 1028
sym_shift = 0

# Input data
input_data = np.array([10, 20, 30, 40, 50], dtype=np.int32)

# Encode
encoded = rc.encode(input_data, cum_freqs, freqs, tot_freq, sym_shift)

# Decode
decoded = rc.decode(encoded, len(input_data), cum_freqs, freqs, tot_freq, sym_shift)
```
