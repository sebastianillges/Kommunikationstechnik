import random

import numpy as np

from block_codes import BlockCodes
from channel import BSC
from channel import FBC


class Source:

    def __init__(self, k):
        self.k = k

    def __call__(self):
        random_message = np.random.randint(2, size=self.k)
        print(f"Random Message: {random_message}")
        return random_message


class Sender:

    def __init__(self, block_code):
        self.block_code = block_code

    def __call__(self, message):
        encoded_message = self.block_code.encode(message)
        print(f"Encoded Message: {encoded_message}")
        return encoded_message


class Channel:

    def __init__(self, channel):
        self.channel = channel

    def __call__(self, message):
        faulty_message, num_errors = self.channel.__call__(message)
        print(f"Faulty Message: {faulty_message}\nNumber of Errors: {num_errors}")
        return faulty_message


class Receiver:

    def __init__(self, block_code):
        self.block_code = block_code

    def __call__(self, recv_message):
        corrected_message = self.block_code.decode(recv_message)
        print(f"Corrected Message: {corrected_message[0]}\n")
        return corrected_message


def diff(correct, faulty):
    return sum([1 for c, f in zip(correct, faulty) if c != f])


class Simulation:

    def __init__(self, source, sender, channel, receiver):
        self.source = source
        self.sender = sender
        self.channel = channel
        self.receiver = receiver

    def __call__(self, num_messages):
        results = []
        for message in range(num_messages):
            random_message = self.source()
            encoded_message = self.sender(random_message)
            faulty_message = self.channel(encoded_message)
            num_wrong_bits_before = diff(random_message, faulty_message)
            error_correction = False
            corrected_message, num_corrections = self.receiver(faulty_message)
            if corrected_message is not None:
                error_correction = True
            num_not_corrected = diff(random_message, corrected_message)
            results.append((num_wrong_bits_before, error_correction, num_corrections, num_not_corrected))
        return results


if __name__ == '__main__':
    block_code = BlockCodes([[1, 1, 0], [0, 1, 1], [1, 1, 1], [1, 0, 1]], 1)
    sim = Simulation(Source(4),
                     Sender(block_code),
                     Channel(BSC(0.2)),
                     Receiver(block_code))
    results = sim(10)