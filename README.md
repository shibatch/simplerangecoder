# Simple Range Coder

A simple range coding library implemented in C++20 with a Python wrapper. While simple, it provides better performance than a pure Python implementation. This component provides entropy encoding and decoding for signed integer arrays.

## License

This project is licensed under [CC0 1.0 Universal](LICENSE).

## Features

- **Algorithm**: Schindler's 32-bit top-down range coder.
- **Precision**: 32-bit range, 64-bit low.
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

### Python API (`SimpleRangeCoder`)

#### `encode(q_vals, cum_freqs, freqs, tot_freq, sym_shift)`
- `q_vals`: NumPy array (int32) of values to compress.
- Returns: `bytes` object containing the compressed stream.

#### `decode(data_bytes, block_len, cum_freqs, freqs, tot_freq, sym_shift)`
- `data_bytes`: `bytes` object to decompress.
- `block_len`: Expected number of symbols.
- Returns: NumPy array (int32) of reconstructed values.

## Usage Example (Python)

```python
import numpy as np
from fast_rc import SimpleRangeCoder

rc = SimpleRangeCoder("./librangecoder.so")
# ... define freqs, cum_freqs, etc. ...
encoded = rc.encode(input_data, cum_freqs, freqs, tot_freq, sym_shift)
decoded = rc.decode(encoded, len(input_data), cum_freqs, freqs, tot_freq, sym_shift)
```
