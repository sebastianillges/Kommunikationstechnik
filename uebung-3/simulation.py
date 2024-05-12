import matplotlib.pyplot as plt
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
        if corrected_message:
            print(f"Corrected Message: {corrected_message[0]}")
        return corrected_message


def diff(correct, faulty):
    return sum([1 for c, f in zip(correct, faulty) if c != f])


def eval(results):
    num_messages = len(results)
    num_correct_transmissions = 0
    num_corrections = 0
    num_uncorrected = 0
    num_correct_corrections = 0
    num_wrong_corrections = 0
    num_bits_before_corrections = 0
    num_corrected_bits = 0
    num_uncorrected_bits = 0
    for result in results:
        # 1. number of correct transmissions
        if diff(result[1], result[2]) == 0:
            num_correct_transmissions += 1
        # 2. number of corrected messages
        if result[5]:
            num_corrections += 1
        # 3. number of correct corrections
        if result[5] and diff(result[0], result[3]) == 0:
            num_correct_corrections += 1
        # 4. number of wrong corrections
        elif result[5] and diff(result[0], result[3]) != 0:
            num_wrong_corrections += 1
        # 6. number of bit errors before correction
        num_bits_before_corrections += result[4]
        # 7. number of uncorrected bits
        num_corrected_bits += result[6]
        # 8. number of uncorrected bits
        num_uncorrected_bits += result[7]

    print(f"Number of correct Transmissions: {num_correct_transmissions}/{num_messages}")
    print(f"Number of corrected Messages: {num_corrections}/{num_messages}")
    print(f"Number of uncorrected Messages: {num_uncorrected}/{num_messages}")
    print(f"Number of correct Corrections: {num_correct_corrections}/{num_corrections}")
    print(f"Number of wrong Corrections: {num_wrong_corrections}/{num_corrections}")
    print(f"Number of bit errors before correction: {num_bits_before_corrections}")
    print(f"Number of corrected bits: {num_corrected_bits}")
    print(f"Number of uncorrected bits: {num_uncorrected_bits}")

    plt.bar(['flawless messages', 'corrected messages', 'not corrected messages'],
            [num_correct_transmissions, num_corrections, num_uncorrected])
    plt.xlabel('messages')
    plt.show()

    plt.bar(['flawless messages', 'successfully corrected messages', 'wrong corrected messages'],
            [num_correct_transmissions, num_correct_corrections, num_wrong_corrections])
    plt.xlabel('messages')
    plt.xticks(rotation=5)
    plt.show()

    plt.bar(['bit errors before correction', 'corrected bits', 'bit errors after correction'],
            [num_bits_before_corrections, num_corrected_bits, num_uncorrected_bits])
    plt.xlabel('bit errors')
    plt.show()


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
            corrected = self.receiver(faulty_message)
            if corrected:
                corrected_message, num_corrections = corrected
                if num_corrections > 0:
                    error_correction = True
                num_not_corrected = diff(random_message, corrected_message)
                results.append((random_message, encoded_message, faulty_message, corrected_message, num_wrong_bits_before,
                                error_correction, num_corrections, num_not_corrected))
                if diff(random_message, corrected_message) == 0:
                    print("Corrected")
                else:
                    print("Not Corrected")
                print()
        return results


if __name__ == '__main__':
    # Scenario 1 Hamming-Code
    block_code = BlockCodes([[1, 1, 0], [0, 1, 1], [1, 1, 1], [1, 0, 1]], 1)
    sim = Simulation(Source(4),
                     Sender(block_code),
                     Channel(BSC(0.05)),
                     Receiver(block_code))
    results = sim(1000)
    eval(results)

    # Scenario 2
    block_code = BlockCodes([[1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 1]], 2)
    sim = Simulation(Source(3),
                     Sender(block_code),
                     Channel(BSC(0.15)),
                     Receiver(block_code))
    results = sim(1000)
    eval(results)

    # Scenario 3
    block_code = BlockCodes([[1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 1]], 2)
    sim = Simulation(Source(3),
                     Sender(block_code),
                     Channel(BSC(0.001)),
                     Receiver(block_code))
    results = sim(1000)
    eval(results)

    sim = Simulation(Source(3),
                     Sender(block_code),
                     Channel(BSC(0.2)),
                     Receiver(block_code))
    results = sim(1000)
    eval(results)
