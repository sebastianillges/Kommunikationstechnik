# channel.py

import numpy as np


# binary symmetrical channel
class BSC:
    def __init__(self, probability):
        self.probability = probability

    def __call__(self, codeword):
        mask = np.array([1 if self.probability > np.random.rand() else 0 for bit in codeword])
        return codeword ^ mask


# fixed bit error channel
class FBC:
    def __init__(self, num_bits):
        self.num_bits = num_bits

    def __call__(self, codeword):
        indices = np.random.choice(len(codeword), self.num_bits, replace=False)
        codeword[indices] = 1 - codeword[indices]
        return codeword


if __name__ == '__main__':
    bsc = BSC(0.2)
    print(bsc(np.zeros(10, dtype=int)))

    fbc = FBC(2)
    print(fbc(np.zeros(10, dtype=int)))
