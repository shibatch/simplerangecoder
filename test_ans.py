import unittest
import numpy as np
from fast_rc import SimpleRangeCoder

class TestANSCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rc = SimpleRangeCoder("./librangecoder.so")
        # For rANS, tot_freq must be 2^16 = 65536
        cls.tot_freq = 65536
        cls.alphabet_size = 256
        cls.sym_shift = 0

        # Create a probability model where tot_freq = 65536
        cls.freqs = np.full(cls.alphabet_size, cls.tot_freq // cls.alphabet_size, dtype=np.int32)
        # Adjust last element to ensure sum is exactly 65536
        cls.freqs[-1] += cls.tot_freq - np.sum(cls.freqs)

        cls.cum_freqs = np.zeros(cls.alphabet_size + 1, dtype=np.int32)
        cls.cum_freqs[1:] = np.cumsum(cls.freqs)

    def run_roundtrip(self, num_vals):
        q_vals = np.random.randint(0, self.alphabet_size, size=num_vals, dtype=np.int32)

        encoded = self.rc.ans_encode(
            q_vals, self.cum_freqs, self.freqs, self.tot_freq, self.sym_shift
        )

        decoded = self.rc.ans_decode(
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

class TestBatchANSCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rc = SimpleRangeCoder("./librangecoder.so")

    def test_batch_vs_serial(self):
        num_blocks = 8
        block_size = 1024
        num_models = 4
        alphabet_size = 256
        tot_freq = 65536

        # Create multiple models
        lut_freqs = np.random.randint(1, 100, size=(num_models, alphabet_size), dtype=np.int32)
        lut_cum_freqs = np.zeros((num_models, alphabet_size + 1), dtype=np.int32)
        for i in range(num_models):
            # Scale to tot_freq
            s = np.sum(lut_freqs[i])
            lut_freqs[i] = (lut_freqs[i].astype(np.float64) * tot_freq / s).astype(np.int32)
            lut_freqs[i][lut_freqs[i] == 0] = 1 # Ensure no zero freq
            lut_freqs[i][-1] += tot_freq - np.sum(lut_freqs[i])
            lut_cum_freqs[i, 1:] = np.cumsum(lut_freqs[i])

        # Prepare batch data
        all_q_vals = np.random.randint(0, alphabet_size, size=(num_blocks, block_size), dtype=np.int32)
        all_decay_indices = np.random.randint(0, num_models, size=num_blocks, dtype=np.int32)
        all_alphabet_sizes = np.full(num_blocks, alphabet_size, dtype=np.int32)
        batch_tot_freqs = np.full(num_blocks, tot_freq, dtype=np.int32)
        all_sym_shifts = np.zeros(num_blocks, dtype=np.int32)

        # Batch encode
        batch_encoded_bufs, batch_encoded_sizes = self.rc.batch_ans_encode(
            all_q_vals, lut_cum_freqs, lut_freqs, alphabet_size,
            all_decay_indices, all_alphabet_sizes, batch_tot_freqs, all_sym_shifts
        )

        # Serial encode and verify
        for i in range(num_blocks):
            decay_idx = all_decay_indices[i]
            encoded = self.rc.ans_encode(
                all_q_vals[i],
                lut_cum_freqs[decay_idx],
                lut_freqs[decay_idx],
                batch_tot_freqs[i],
                all_sym_shifts[i]
            )
            # Check bit-for-bit identity
            self.assertEqual(encoded, bytes(batch_encoded_bufs[i, :batch_encoded_sizes[i]]))

        # Batch decode
        decoded_q_vals, ret_codes = self.rc.batch_ans_decode(
            batch_encoded_bufs, batch_encoded_sizes, block_size,
            lut_cum_freqs, lut_freqs, alphabet_size,
            all_decay_indices, all_alphabet_sizes, batch_tot_freqs, all_sym_shifts
        )

        # Verify decoded data
        for i in range(num_blocks):
            self.assertEqual(ret_codes[i], 0, f"Block {i} failed with code {ret_codes[i]}")
            np.testing.assert_array_equal(all_q_vals[i], decoded_q_vals[i])

if __name__ == "__main__":
    unittest.main()
