#ifndef RANGE_CODER_H
#define RANGE_CODER_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Range Encode Interface
 *
 * @param q_vals Input array of signed integers.
 * @param num_vals Number of elements in q_vals.
 * @param cum_freqs Cumulative frequency array (size: alphabet_size + 1).
 * @param freqs Individual frequency array (size: alphabet_size).
 * @param alphabet_size Maximum number of buckets.
 * @param tot_freq Sum of frequencies (must match cum_freqs[alphabet_size]).
 * @param sym_shift Offset to convert q_val to positive index (sym = q_val + sym_shift).
 * @param out_buf Output buffer for compressed byte stream.
 * @param out_buf_len Maximum size of out_buf.
 * @return int32_t Number of bytes written, or -1 on error (e.g., buffer overflow).
 */
int32_t range_encode_interface(
    const int32_t* q_vals,
    int32_t num_vals,
    const int32_t* cum_freqs,
    const int32_t* freqs,
    int32_t alphabet_size,
    int32_t tot_freq,
    int32_t sym_shift,
    uint8_t* out_buf,
    int32_t out_buf_len
);

/**
 * @brief Range Decode Interface
 *
 * @param data Compressed byte stream.
 * @param data_len Length of data in bytes.
 * @param block_len Number of elements to reconstruct.
 * @param cum_freqs Cumulative frequency array.
 * @param freqs Individual frequency array.
 * @param alphabet_size Maximum number of buckets.
 * @param tot_freq Sum of frequencies.
 * @param sym_shift Offset used during encoding.
 * @param out_q_vals Output array for reconstructed integers.
 * @return int32_t 0 on success, or negative error code.
 */
int32_t range_decode_interface(
    const uint8_t* data,
    int32_t data_len,
    int32_t block_len,
    const int32_t* cum_freqs,
    const int32_t* freqs,
    int32_t alphabet_size,
    int32_t tot_freq,
    int32_t sym_shift,
    int32_t* out_q_vals
);

#ifdef __cplusplus
}
#endif

#endif // RANGE_CODER_H
