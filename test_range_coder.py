import unittest
import numpy as np
from fast_rc import SimpleRangeCoder

class TestRangeCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rc = SimpleRangeCoder("./librangecoder.so")
        cls.alphabet_size = 257
        cls.freq_val = 4
        cls.tot_freq = cls.alphabet_size * cls.freq_val
        cls.sym_shift = 0
        cls.freqs = np.full(cls.alphabet_size, cls.freq_val, dtype=np.int32)
        cls.cum_freqs = np.zeros(cls.alphabet_size + 1, dtype=np.int32)
        cls.cum_freqs[1:] = np.cumsum(cls.freqs)

    def run_roundtrip(self, num_vals):
        q_vals = np.random.randint(0, self.alphabet_size, size=num_vals, dtype=np.int32)

        encoded = self.rc.encode(
            q_vals, self.cum_freqs, self.freqs, self.tot_freq, self.sym_shift
        )

        decoded = self.rc.decode(
            encoded, num_vals, self.cum_freqs, self.freqs, self.tot_freq, self.sym_shift
        )

        np.testing.assert_array_equal(q_vals, decoded)

    def test_small(self):
        self.run_roundtrip(4)

    def test_medium(self):
        self.run_roundtrip(4096)

    def test_large(self):
        self.run_roundtrip(16384)

    def test_empty(self):
        self.run_roundtrip(0)

    def test_zero_data_len(self):
        # Specific behavior test for data_len <= 0
        block_len = 10
        decoded = self.rc.decode(b"", block_len, self.cum_freqs, self.freqs, self.tot_freq, self.sym_shift)
        expected = np.zeros(block_len, dtype=np.int32)
        np.testing.assert_array_equal(decoded, expected)

if __name__ == "__main__":
    unittest.main()
