# convolutional_code.py

import numpy as np
from komm import ConvolutionalCode, TerminatedConvolutionalCode, BlockEncoder, BlockDecoder
import matplotlib.pyplot as plt

np.set_printoptions(linewidth=200)


# Encode a list of frames.
def decode_frames(frames, code):
    # return np.array(list(map(BlockDecoder(code, method='viterbi_soft'), frames)))
    return np.array(list(map(BlockDecoder(code, method='viterbi_hard'), frames)))


# Return a list of frames where bits are flipped with a specified probability.
def bit_errors(frames, bit_error_probability, rng):
    return np.array([frame ^ (bit_error_probability > rng.random(len(frame))) for frame in frames])


# Encode a list of frames.
def encode_frames(frames, code):
    return np.array(list(map(BlockEncoder(code), frames)))


# Generate a list of frames with fixed length and random bit values.
def gen_random_frames(frame_length, number_of_frames, rng):
    return rng.integers(0, 2, (number_of_frames, frame_length))


def simulate_cc(code_repr, frame_length, number_of_frames, bit_error_probability, seed, print_results=False):
    # random number generator
    rng = np.random.default_rng(seed)

    # setup convolutional code
    code = TerminatedConvolutionalCode(ConvolutionalCode(code_repr), num_blocks=frame_length)

    # generate random frames
    frames = gen_random_frames(frame_length, number_of_frames, rng)

    # encode frames using convolutional codes
    frames_encoded = encode_frames(frames, code)

    # introduce bit errors
    frames_encoded_error = bit_errors(frames_encoded, bit_error_probability, rng)

    # decode frames with error correction
    frames_decoded = decode_frames(frames_encoded_error, code)

    if print_results:
        print('frames:', frames, sep='\n', end='\n\n')
        print('encoded frames:', frames_encoded, sep='\n', end='\n\n')
        print('encoded frames with bit errors:', frames_encoded_error, sep='\n', end='\n\n')
        print('decoded frames:', frames_decoded, sep='\n', end='\n\n')

    # determine frame error rate
    frame_error_rate = np.mean(np.any(frames != frames_decoded, axis=1))
    return frame_error_rate


def simulations_studie():
    codes = {
        "1/3": [[0o155, 0o173, 0o157]],
        "1/2": [[0o133, 0o171]],
        "2/3": [[0o15, 0o17, 0o13]],
        "3/4": [[0o17, 0o15, 0o13, 0o11]]
    }
    bers = [0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2]
    frame_length = 64
    number_of_frames = 100

    frame_error_rate_results = {}
    throughput_results = {}

    for rate, code in codes.items():
        code_fer = []
        code_throughput = []
        for err in bers:
            print(f"Rate: {rate}, Code: {code} with error rate: {err}")
            fer = simulate_cc(code_repr=code, frame_length=frame_length, number_of_frames=number_of_frames,
                            bit_error_probability=err, seed=1)
            throughput = float(rate.split('/')[0]) / float(rate.split('/')[1]) * (1 - fer)
            code_fer.append(fer)
            code_throughput.append(throughput)
        frame_error_rate_results[rate] = code_fer
        throughput_results[rate] = code_throughput

    plt.figure(figsize=(14, 6))

    # Plot FER vs BER
    plt.subplot(1, 2, 1)
    for rate in codes.keys():
        label = f"Rate {rate} ({', '.join(map(lambda x: oct(x), codes[rate][0]))})"
        plt.plot(bers, frame_error_rate_results[rate], label=label)
    plt.xlabel('Bit Error Rate')
    plt.ylabel('Frame Error Rate')
    plt.legend()
    plt.title('FER vs. BER')

    # Plot Throughput vs BER
    plt.subplot(1, 2, 2)
    for rate in codes.keys():
        label = f"Rate {rate} ({', '.join(map(lambda x: oct(x), codes[rate][0]))})"
        plt.plot(bers, throughput_results[rate], label=label)
    plt.xlabel('Bit Error Rate')
    plt.ylabel('Throughput')
    plt.legend()
    plt.title('Durchsatz vs. BER')

    plt.tight_layout()
    plt.show()


def main():
    simulations_studie()


if __name__ == '__main__':
    main()
