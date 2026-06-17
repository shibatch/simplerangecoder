import ctypes
import numpy as np
import os

class SimpleRangeCoder:
    def __init__(self, lib_path="./librangecoder.so"):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found at {lib_path}")

        self.lib = ctypes.CDLL(lib_path)

        # Define range_encode_interface
        self.lib.range_encode_interface.argtypes = [
            ctypes.POINTER(ctypes.c_int32), # q_vals
            ctypes.c_int32,                # num_vals
            ctypes.POINTER(ctypes.c_int32), # cum_freqs
            ctypes.POINTER(ctypes.c_int32), # freqs
            ctypes.c_int32,                # alphabet_size
            ctypes.c_int32,                # tot_freq
            ctypes.c_int32,                # sym_shift
            ctypes.POINTER(ctypes.c_uint8), # out_buf
            ctypes.c_int32                 # out_buf_len
        ]
        self.lib.range_encode_interface.restype = ctypes.c_int32

        # Define range_decode_interface
        self.lib.range_decode_interface.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), # data
            ctypes.c_int32,                # data_len
            ctypes.c_int32,                # block_len
            ctypes.POINTER(ctypes.c_int32), # cum_freqs
            ctypes.POINTER(ctypes.c_int32), # freqs
            ctypes.c_int32,                # alphabet_size
            ctypes.c_int32,                # tot_freq
            ctypes.c_int32,                # sym_shift
            ctypes.POINTER(ctypes.c_int32)  # out_q_vals
        ]
        self.lib.range_decode_interface.restype = ctypes.c_int32

        # Define range_encode_batch
        self.lib.range_encode_batch.argtypes = [
            ctypes.c_int32,                 # num_blocks
            ctypes.POINTER(ctypes.c_int32),  # all_q_vals
            ctypes.c_int32,                 # block_size
            ctypes.POINTER(ctypes.c_int32),  # lut_cum_freqs
            ctypes.POINTER(ctypes.c_int32),  # lut_freqs
            ctypes.c_int32,                 # max_alphabet_size
            ctypes.POINTER(ctypes.c_int32),  # all_decay_indices
            ctypes.POINTER(ctypes.c_int32),  # all_alphabet_sizes
            ctypes.POINTER(ctypes.c_int32),  # all_tot_freqs
            ctypes.POINTER(ctypes.c_int32),  # all_sym_shifts
            ctypes.POINTER(ctypes.c_uint8),  # all_output_buffers
            ctypes.c_int32,                 # max_output_size_per_block
            ctypes.POINTER(ctypes.c_int32)   # all_output_sizes
        ]
        self.lib.range_encode_batch.restype = None

        # Define range_decode_batch
        self.lib.range_decode_batch.argtypes = [
            ctypes.c_int32,                 # num_blocks
            ctypes.POINTER(ctypes.c_uint8),  # all_compressed_data
            ctypes.c_int32,                 # max_output_size_per_block
            ctypes.POINTER(ctypes.c_int32),  # all_compressed_lengths
            ctypes.c_int32,                 # block_size
            ctypes.POINTER(ctypes.c_int32),  # lut_cum_freqs
            ctypes.POINTER(ctypes.c_int32),  # lut_freqs
            ctypes.c_int32,                 # max_alphabet_size
            ctypes.POINTER(ctypes.c_int32),  # all_decay_indices
            ctypes.POINTER(ctypes.c_int32),  # all_alphabet_sizes
            ctypes.POINTER(ctypes.c_int32),  # all_tot_freqs
            ctypes.POINTER(ctypes.c_int32),  # all_sym_shifts
            ctypes.POINTER(ctypes.c_int32),  # all_out_q_vals
            ctypes.POINTER(ctypes.c_int32)   # all_ret_codes
        ]
        self.lib.range_decode_batch.restype = None

        # Define rANS interfaces
        self.lib.ans_encode_interface.argtypes = self.lib.range_encode_interface.argtypes
        self.lib.ans_encode_interface.restype = self.lib.range_encode_interface.restype
        self.lib.ans_decode_interface.argtypes = self.lib.range_decode_interface.argtypes
        self.lib.ans_decode_interface.restype = self.lib.range_decode_interface.restype
        self.lib.ans_encode_batch.argtypes = self.lib.range_encode_batch.argtypes
        self.lib.ans_encode_batch.restype = self.lib.range_encode_batch.restype
        self.lib.ans_decode_batch.argtypes = self.lib.range_decode_batch.argtypes
        self.lib.ans_decode_batch.restype = self.lib.range_decode_batch.restype

    def encode(self, q_vals, cum_freqs, freqs, tot_freq, sym_shift):
        q_vals = np.ascontiguousarray(q_vals, dtype=np.int32)
        cum_freqs = np.ascontiguousarray(cum_freqs, dtype=np.int32)
        freqs = np.ascontiguousarray(freqs, dtype=np.int32)

        num_vals = len(q_vals)
        alphabet_size = len(freqs)

        # Buffer size requirement: num_vals * 4 + 64 bytes
        out_buf_len = num_vals * 4 + 64
        out_buf = np.zeros(out_buf_len, dtype=np.uint8)

        written = self.lib.range_encode_interface(
            q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            num_vals,
            cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            alphabet_size,
            tot_freq,
            sym_shift,
            out_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            out_buf_len
        )

        if written < 0:
            raise RuntimeError("Range encoding failed (possibly buffer overflow)")

        return bytes(out_buf[:written])

    def decode(self, data_bytes, block_len, cum_freqs, freqs, tot_freq, sym_shift):
        if not isinstance(data_bytes, bytes):
            data_bytes = bytes(data_bytes)

        cum_freqs = np.ascontiguousarray(cum_freqs, dtype=np.int32)
        freqs = np.ascontiguousarray(freqs, dtype=np.int32)

        alphabet_size = len(freqs)
        out_q_vals = np.zeros(block_len, dtype=np.int32)

        data_len = len(data_bytes)
        data_ptr = (ctypes.c_uint8 * data_len).from_buffer_copy(data_bytes)

        ret = self.lib.range_decode_interface(
            data_ptr,
            data_len,
            block_len,
            cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            alphabet_size,
            tot_freq,
            sym_shift,
            out_q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        )

        if ret < 0:
            raise RuntimeError(f"Range decoding failed with error code: {ret}")

        return out_q_vals

    def batch_encode(self, all_q_vals, lut_cum_freqs, lut_freqs, max_alphabet_size,
                     all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts):
        num_blocks, block_size = all_q_vals.shape

        all_q_vals = np.ascontiguousarray(all_q_vals, dtype=np.int32)
        lut_cum_freqs = np.ascontiguousarray(lut_cum_freqs, dtype=np.int32)
        lut_freqs = np.ascontiguousarray(lut_freqs, dtype=np.int32)
        all_decay_indices = np.ascontiguousarray(all_decay_indices, dtype=np.int32)
        all_alphabet_sizes = np.ascontiguousarray(all_alphabet_sizes, dtype=np.int32)
        all_tot_freqs = np.ascontiguousarray(all_tot_freqs, dtype=np.int32)
        all_sym_shifts = np.ascontiguousarray(all_sym_shifts, dtype=np.int32)

        max_output_size_per_block = block_size * 4 + 64
        all_output_buffers = np.zeros((num_blocks, max_output_size_per_block), dtype=np.uint8)
        all_output_sizes = np.zeros(num_blocks, dtype=np.int32)

        self.lib.range_encode_batch(
            num_blocks,
            all_q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            block_size,
            lut_cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            lut_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            max_alphabet_size,
            all_decay_indices.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_alphabet_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_tot_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_sym_shifts.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_output_buffers.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            max_output_size_per_block,
            all_output_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        )

        return all_output_buffers, all_output_sizes

    def batch_decode(self, all_compressed_data, all_compressed_lengths, block_size,
                     lut_cum_freqs, lut_freqs, max_alphabet_size,
                     all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts):
        num_blocks = len(all_compressed_lengths)
        max_output_size_per_block = all_compressed_data.shape[1]

        all_compressed_data = np.ascontiguousarray(all_compressed_data, dtype=np.uint8)
        all_compressed_lengths = np.ascontiguousarray(all_compressed_lengths, dtype=np.int32)
        lut_cum_freqs = np.ascontiguousarray(lut_cum_freqs, dtype=np.int32)
        lut_freqs = np.ascontiguousarray(lut_freqs, dtype=np.int32)
        all_decay_indices = np.ascontiguousarray(all_decay_indices, dtype=np.int32)
        all_alphabet_sizes = np.ascontiguousarray(all_alphabet_sizes, dtype=np.int32)
        all_tot_freqs = np.ascontiguousarray(all_tot_freqs, dtype=np.int32)
        all_sym_shifts = np.ascontiguousarray(all_sym_shifts, dtype=np.int32)

        all_out_q_vals = np.zeros((num_blocks, block_size), dtype=np.int32)
        all_ret_codes = np.zeros(num_blocks, dtype=np.int32)

        self.lib.range_decode_batch(
            num_blocks,
            all_compressed_data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            max_output_size_per_block,
            all_compressed_lengths.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            block_size,
            lut_cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            lut_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            max_alphabet_size,
            all_decay_indices.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_alphabet_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_tot_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_sym_shifts.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_out_q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_ret_codes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        )

        return all_out_q_vals, all_ret_codes

    def ans_encode(self, q_vals, cum_freqs, freqs, tot_freq, sym_shift):
        q_vals = np.ascontiguousarray(q_vals, dtype=np.int32)
        cum_freqs = np.ascontiguousarray(cum_freqs, dtype=np.int32)
        freqs = np.ascontiguousarray(freqs, dtype=np.int32)

        num_vals = len(q_vals)
        alphabet_size = len(freqs)

        out_buf_len = num_vals * 4 + 64
        out_buf = np.zeros(out_buf_len, dtype=np.uint8)

        written = self.lib.ans_encode_interface(
            q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            num_vals,
            cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            alphabet_size,
            tot_freq,
            sym_shift,
            out_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            out_buf_len
        )

        if written < 0:
            raise RuntimeError("rANS encoding failed (possibly buffer overflow)")

        return bytes(out_buf[:written])

    def ans_decode(self, data_bytes, block_len, cum_freqs, freqs, tot_freq, sym_shift):
        if not isinstance(data_bytes, bytes):
            data_bytes = bytes(data_bytes)

        cum_freqs = np.ascontiguousarray(cum_freqs, dtype=np.int32)
        freqs = np.ascontiguousarray(freqs, dtype=np.int32)

        alphabet_size = len(freqs)
        out_q_vals = np.zeros(block_len, dtype=np.int32)

        data_len = len(data_bytes)
        data_ptr = (ctypes.c_uint8 * data_len).from_buffer_copy(data_bytes)

        ret = self.lib.ans_decode_interface(
            data_ptr,
            data_len,
            block_len,
            cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            alphabet_size,
            tot_freq,
            sym_shift,
            out_q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        )

        if ret < 0:
            raise RuntimeError(f"rANS decoding failed with error code: {ret}")

        return out_q_vals

    def batch_ans_encode(self, all_q_vals, lut_cum_freqs, lut_freqs, max_alphabet_size,
                         all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts):
        num_blocks, block_size = all_q_vals.shape

        all_q_vals = np.ascontiguousarray(all_q_vals, dtype=np.int32)
        lut_cum_freqs = np.ascontiguousarray(lut_cum_freqs, dtype=np.int32)
        lut_freqs = np.ascontiguousarray(lut_freqs, dtype=np.int32)
        all_decay_indices = np.ascontiguousarray(all_decay_indices, dtype=np.int32)
        all_alphabet_sizes = np.ascontiguousarray(all_alphabet_sizes, dtype=np.int32)
        all_tot_freqs = np.ascontiguousarray(all_tot_freqs, dtype=np.int32)
        all_sym_shifts = np.ascontiguousarray(all_sym_shifts, dtype=np.int32)

        max_output_size_per_block = block_size * 4 + 64
        all_output_buffers = np.zeros((num_blocks, max_output_size_per_block), dtype=np.uint8)
        all_output_sizes = np.zeros(num_blocks, dtype=np.int32)

        self.lib.ans_encode_batch(
            num_blocks,
            all_q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            block_size,
            lut_cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            lut_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            max_alphabet_size,
            all_decay_indices.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_alphabet_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_tot_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_sym_shifts.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_output_buffers.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            max_output_size_per_block,
            all_output_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        )

        return all_output_buffers, all_output_sizes

    def batch_ans_decode(self, all_compressed_data, all_compressed_lengths, block_size,
                         lut_cum_freqs, lut_freqs, max_alphabet_size,
                         all_decay_indices, all_alphabet_sizes, all_tot_freqs, all_sym_shifts):
        num_blocks = len(all_compressed_lengths)
        max_output_size_per_block = all_compressed_data.shape[1]

        all_compressed_data = np.ascontiguousarray(all_compressed_data, dtype=np.uint8)
        all_compressed_lengths = np.ascontiguousarray(all_compressed_lengths, dtype=np.int32)
        lut_cum_freqs = np.ascontiguousarray(lut_cum_freqs, dtype=np.int32)
        lut_freqs = np.ascontiguousarray(lut_freqs, dtype=np.int32)
        all_decay_indices = np.ascontiguousarray(all_decay_indices, dtype=np.int32)
        all_alphabet_sizes = np.ascontiguousarray(all_alphabet_sizes, dtype=np.int32)
        all_tot_freqs = np.ascontiguousarray(all_tot_freqs, dtype=np.int32)
        all_sym_shifts = np.ascontiguousarray(all_sym_shifts, dtype=np.int32)

        all_out_q_vals = np.zeros((num_blocks, block_size), dtype=np.int32)
        all_ret_codes = np.zeros(num_blocks, dtype=np.int32)

        self.lib.ans_decode_batch(
            num_blocks,
            all_compressed_data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),
            max_output_size_per_block,
            all_compressed_lengths.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            block_size,
            lut_cum_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            lut_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            max_alphabet_size,
            all_decay_indices.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_alphabet_sizes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_tot_freqs.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_sym_shifts.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_out_q_vals.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
            all_ret_codes.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        )

        return all_out_q_vals, all_ret_codes
