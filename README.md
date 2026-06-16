# Simple Range Coder

A simple range coding library implemented in C++20 with a Python wrapper. While simple, it provides better performance than a pure Python implementation. This component provides entropy encoding and decoding for signed integer arrays.

## License

This project is licensed under [CC0 1.0 Universal](LICENSE).

## Features

- **Algorithm**: Schindler's 32-bit top-down range coder.
- **Precision**: 32-bit range, 64-bit low.
- **Parallelization**: OpenMP-accelerated batch encoding and decoding.
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

#### `range_encode_interface`
Encodes an array of integers into a byte stream.

```cpp
int32_t range_encode_interface(
    const int32_t* q_vals,    // Input integers
    int32_t num_vals,         // Number of input integers
    const int32_t* cum_freqs, // Cumulative frequencies (alphabet_size + 1)
    const int32_t* freqs,     // Individual frequencies (alphabet_size)
    int32_t alphabet_size,    // Number of possible symbols
    int32_t tot_freq,         // Sum of frequencies
    int32_t sym_shift,        // Offset: sym = q_val + sym_shift
    uint8_t* out_buf,         // Output buffer
    int32_t out_buf_len       // Output buffer capacity
);
```
**Returns**: Number of bytes written, or `-1` on failure (e.g., buffer overflow).

#### `range_decode_interface`
Decodes a byte stream back into integers.

```cpp
int32_t range_decode_interface(
    const uint8_t* data,      // Compressed byte stream
    int32_t data_len,         // Length of input data
    int32_t block_len,        // Number of elements to decode
    const int32_t* cum_freqs, // Cumulative frequencies
    const int32_t* freqs,     // Individual frequencies
    int32_t alphabet_size,    // Number of symbols
    int32_t tot_freq,         // Sum of frequencies
    int32_t sym_shift,        // Same offset as used in encoding
    int32_t* out_q_vals       // Output array for integers
);
```
**Returns**: `0` on success, negative error code on failure.

#### `range_encode_batch`
Encodes multiple blocks in parallel using OpenMP.

```cpp
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
```

#### `range_decode_batch`
Decodes multiple blocks in parallel using OpenMP.

```cpp
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
```

### Python API (`SimpleRangeCoder`)

#### `encode(q_vals, cum_freqs, freqs, tot_freq, sym_shift)`
- `q_vals`: NumPy array (int32) of values to compress.
- Returns: `bytes` object containing the compressed stream.

#### `decode(data_bytes, block_len, cum_freqs, freqs, tot_freq, sym_shift)`
- `data_bytes`: `bytes` object to decompress.
- `block_len`: Expected number of symbols.
- Returns: NumPy array (int32) of reconstructed values.

#### `batch_encode(...)`
Encodes a batch of blocks.
- Returns: `(all_output_buffers, all_output_sizes)`

#### `batch_decode(...)`
Decodes a batch of blocks.
- Returns: `(all_out_q_vals, all_ret_codes)`

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
