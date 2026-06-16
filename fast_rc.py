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
