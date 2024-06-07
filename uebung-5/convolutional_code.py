# convolutional_code.py

import random

import komm
import numpy as np
from komm import ConvolutionalCode, TerminatedConvolutionalCode, BlockEncoder, BlockDecoder


# Encode a list of frames.
def decode_frames(frames, code):
    return np.array(list(map(BlockDecoder(code, method='viterbi_soft'), frames)))


# Return a list of frames where bits are flipped with a specified probability.
def bit_errors(frames, bit_error_probability, rng):
    return np.array([frame ^ (bit_error_probability > rng.random(len(frame))) for frame in frames])


# Encode a list of frames.
def encode_frames(frames, code):
    return np.array(list(map(BlockEncoder(code), frames)))


# Generate a list of frames with fixed length and random bit values.
def gen_random_frames(frame_length, number_of_frames, rng):
    return rng.integers(0, 2, (number_of_frames, frame_length))


def simulate_cc(code_repr, frame_length, number_of_frames, bit_error_probability, seed):
    # random number generator
    rng = np.random.default_rng(seed)

    # setup convolutional code
    code = TerminatedConvolutionalCode(ConvolutionalCode(code_repr), num_blocks=frame_length)

    # generate random frames
    frames = gen_random_frames(frame_length, number_of_frames, rng)
    print('frames:', frames, sep='\n', end='\n\n')

    # encode frames using convolutional codes
    frames_encoded = encode_frames(frames, code)
    print('encoded frames:', frames_encoded, sep='\n', end='\n\n')

    # introduce bit errors
    frames_encoded_error = bit_errors(frames_encoded, bit_error_probability, rng)
    print('encoded frames with bit errors:', frames_encoded_error, sep='\n', end='\n\n')

    # decode frames with error correction
    frames_decoded = decode_frames(frames_encoded_error, code)
    print('decoded frames:', frames_decoded, sep='\n', end='\n\n')

    # determine frame error rate


def main():
    simulate_cc(code_repr=[[0o133, 0o171]], frame_length=8, number_of_frames=5, bit_error_probability=0.05, seed=1)


if __name__ == '__main__':
    main()
