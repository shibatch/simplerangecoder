import unittest
import numpy as np
from fast_rc import SimpleRangeCoder

class TestBatchRangeCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rc = SimpleRangeCoder("./librangecoder.so")

    def test_batch_vs_serial(self):
        num_blocks = 8
        block_size = 1024
        num_models = 4
        alphabet_size = 257

        # Create multiple models
        lut_freqs = np.random.randint(1, 10, size=(num_models, alphabet_size), dtype=np.int32)
        lut_cum_freqs = np.zeros((num_models, alphabet_size + 1), dtype=np.int32)
        for i in range(num_models):
            lut_cum_freqs[i, 1:] = np.cumsum(lut_freqs[i])

        all_tot_freqs = np.sum(lut_freqs, axis=1, dtype=np.int32)

        # Prepare batch data
        all_q_vals = np.random.randint(0, alphabet_size, size=(num_blocks, block_size), dtype=np.int32)
        all_decay_indices = np.random.randint(0, num_models, size=num_blocks, dtype=np.int32)
        all_alphabet_sizes = np.full(num_blocks, alphabet_size, dtype=np.int32)
        batch_tot_freqs = all_tot_freqs[all_decay_indices]
        all_sym_shifts = np.zeros(num_blocks, dtype=np.int32)

        # Batch encode
        batch_encoded_bufs, batch_encoded_sizes = self.rc.batch_encode(
            all_q_vals, lut_cum_freqs, lut_freqs, alphabet_size,
            all_decay_indices, all_alphabet_sizes, batch_tot_freqs, all_sym_shifts
        )

        # Serial encode and verify
        serial_encoded_list = []
        for i in range(num_blocks):
            decay_idx = all_decay_indices[i]
            encoded = self.rc.encode(
                all_q_vals[i],
                lut_cum_freqs[decay_idx],
                lut_freqs[decay_idx],
                batch_tot_freqs[i],
                all_sym_shifts[i]
            )
            serial_encoded_list.append(encoded)

            # Check bit-for-bit identity
            self.assertEqual(encoded, bytes(batch_encoded_bufs[i, :batch_encoded_sizes[i]]))

        # Batch decode
        decoded_q_vals, ret_codes = self.rc.batch_decode(
            batch_encoded_bufs, batch_encoded_sizes, block_size,
            lut_cum_freqs, lut_freqs, alphabet_size,
            all_decay_indices, all_alphabet_sizes, batch_tot_freqs, all_sym_shifts
        )

        # Verify decoded data
        for i in range(num_blocks):
            self.assertEqual(ret_codes[i], 0)
            np.testing.assert_array_equal(all_q_vals[i], decoded_q_vals[i])

    def test_different_params(self):
        # Test with different alphabet sizes and shifts for each block
        num_blocks = 4
        block_size = 512
        num_models = 2

        max_alphabet_size = 300
        lut_freqs = np.full((num_models, max_alphabet_size), 4, dtype=np.int32)
        lut_cum_freqs = np.zeros((num_models, max_alphabet_size + 1), dtype=np.int32)
        for i in range(num_models):
            lut_cum_freqs[i, 1:] = np.cumsum(lut_freqs[i])

        all_decay_indices = np.array([0, 1, 0, 1], dtype=np.int32)
        all_alphabet_sizes = np.array([100, 200, 250, 300], dtype=np.int32)
        all_sym_shifts = np.array([10, -5, 0, 20], dtype=np.int32)

        # Generate q_vals within respective alphabet sizes
        all_q_vals = np.zeros((num_blocks, block_size), dtype=np.int32)
        for i in range(num_blocks):
            low = -all_sym_shifts[i]
            high = all_alphabet_sizes[i] - all_sym_shifts[i]
            all_q_vals[i] = np.random.randint(low, high, size=block_size, dtype=np.int32)

        all_tot_freqs = np.array([
            lut_cum_freqs[all_decay_indices[i], all_alphabet_sizes[i]]
            for i in range(num_blocks)
        ], dtype=np.int32)

        # Batch encode
        batch_encoded_bufs, batch_encoded_sizes = self.rc.batch_encode(
            all_q_vals, lut_cum_freqs, lut_freqs, max_alphabet_size,
            all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts
        )

        # Batch decode
        decoded_q_vals, ret_codes = self.rc.batch_decode(
            batch_encoded_bufs, batch_encoded_sizes, block_size,
            lut_cum_freqs, lut_freqs, max_alphabet_size,
            all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts
        )

        # Verify
        for i in range(num_blocks):
            self.assertEqual(ret_codes[i], 0)
            np.testing.assert_array_equal(all_q_vals[i], decoded_q_vals[i])

if __name__ == "__main__":
    unittest.main()
