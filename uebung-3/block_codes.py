# block_codes.py

import numpy as np


class BlockCodes:
    def __init__(self, part_matrix, max_corr_bits):
        self.use_bits = np.shape(part_matrix)[0]
        self.code_bits = self.use_bits + np.shape(part_matrix)[1]
        self.check_bits = self.code_bits - self.use_bits
        self.max_corr_bits = max_corr_bits
        self.generator_matrix = np.concatenate((part_matrix, np.identity(self.use_bits)), axis=1).astype(int)
        self.part_matrix = part_matrix
        self.parity_matrix = np.concatenate((np.identity(self.check_bits), np.transpose(self.part_matrix)), axis=1).astype(int)
        self.syndrome_table = np.transpose(self.parity_matrix)

    def encode(self, message):
        check_type_np_int_array(message)
        return message @ self.generator_matrix % 2

    def decode(self, codeword):
        check_type_np_int_array(codeword)
        error_syndrome = codeword @ self.syndrome_table % 2
        corrected_errors = [1 if np.all(n == error_syndrome) else 0 for n in self.syndrome_table]
        message = (codeword ^ corrected_errors)[self.check_bits:]
        return message, sum(corrected_errors)

    def __str__(self):
        return f"""Block Codes Information:
            Use bits: {self.use_bits}
            Code bits: {self.code_bits}
            Check bits: {self.check_bits}
            Maximum correction bits: {self.max_corr_bits}
            Generator matrix:\n{self.generator_matrix}
            Part matrix:\n{self.part_matrix}
            Parity matrix:\n{self.parity_matrix}
            Syndrome table:\n{self.syndrome_table}"""


def check_type_np_int_array(arr):
    if not (isinstance(arr, np.ndarray) and np.issubdtype(arr.dtype, np.integer)):
        raise (ValueError('Argument be a numpy array of ints'))


def test(part_matrix, max_corr_bits):
    bcodes = BlockCodes(part_matrix, max_corr_bits)
    # print(bcodes, end='\n\n')

    message = np.array([0, 1, 1, 0])
    print(f'message: {message}')
    codeword = bcodes.encode(message)
    codeword = np.array([1, 1, 0, 0, 1, 1, 0])
    print(f'sent codeword: {codeword}')

    new_message, corrected_errors = bcodes.decode(codeword)
    print(f'received messsage: {new_message}')
    print(f'number of corrected errors: {corrected_errors}')


def main():
    test(np.array([[1, 1, 0], [0, 1, 1], [1, 1, 1], [1, 0, 1]]), 1)  # Test 1
    # test(np.array([[1, 1, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1]]), 2)  # Test 2
    # test(np.array([[1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 1]]), 2)  # Test 3


if __name__ == '__main__':
    main()
