import numpy as np
from fast_rc import SimpleRangeCoder

def main():
    print("Range Coder Python Hello World")

    rc = SimpleRangeCoder("./librangecoder.so")

    alphabet_size = 257
    freqs = np.full(alphabet_size, 4, dtype=np.int32)
    cum_freqs = np.zeros(alphabet_size + 1, dtype=np.int32)
    cum_freqs[1:] = np.cumsum(freqs)
    tot_freq = 1028
    sym_shift = 0

    input_data = np.array([10, 20, 30, 40, 50], dtype=np.int32)

    encoded = rc.encode(input_data, cum_freqs, freqs, tot_freq, sym_shift)
    print(f"Encoded {len(input_data)} values into {len(encoded)} bytes.")

    decoded = rc.decode(encoded, len(input_data), cum_freqs, freqs, tot_freq, sym_shift)
    print(f"Decoded values: {decoded}")

if __name__ == "__main__":
    main()
