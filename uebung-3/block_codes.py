# block_codes.py

import numpy as np
from itertools import permutations


class BlockCodes:
    def __init__(self, part_matrix, max_corr_bits):
        self.use_bits = np.shape(part_matrix)[0]
        self.code_bits = self.use_bits + np.shape(part_matrix)[1]
        self.check_bits = self.code_bits - self.use_bits
        self.max_corr_bits = max_corr_bits
        self.generator_matrix = np.concatenate((part_matrix, np.identity(self.use_bits)), axis=1).astype(int)
        self.part_matrix = part_matrix
        self.parity_matrix = np.concatenate((np.identity(self.check_bits), np.transpose(self.part_matrix)),
                                            axis=1).astype(int)
        self.parity_matrix_transposed = np.transpose(self.parity_matrix)
        self.syndrome_table = self._build_syndrome_table()
        print("##############################")
        for i, x in self.syndrome_table.items():
            print(i, x)

    def build_syndrome_table(self):
        syndrome_table = [[0] * len(self.parity_matrix_transposed) for _ in range(len(self.parity_matrix_transposed) + 1)]
        for i, column in enumerate(self.parity_matrix_transposed):
            index = int(''.join([f'{b}' for b in column]), 2)
            syndrome_table[index][i] = 1
        return np.array(syndrome_table)

    def _build_syndrome_table(self):
        zero_dict = {0: np.zeros(self.code_bits).astype(int)}
        match self.max_corr_bits:
            case 0:
                return zero_dict
            case 1:
                decimal_values = [int(''.join(map(str, row)), 2) for row in self.parity_matrix_transposed]
                error1 = np.identity(len(decimal_values)).astype(int)
                return {**zero_dict, **dict(sorted(zip(decimal_values, error1)))}
            case 2:
                decimal_values1 = [int(''.join(map(str, row)), 2) for row in self.parity_matrix_transposed]
                e = np.identity(len(decimal_values1)).astype(int)
                error_dict1 = dict(zip(decimal_values1, e))

                # par2 = [(i + j) % 2 for i in self.parity_matrix_transposed for j in self.parity_matrix_transposed]
                # decimal_values2 = [int(''.join(map(str, row)), 2) for row in par2]
                # error2 = [(i + j) % 2 for i in np.identity(len(decimal_values2)).astype(int) for j in np.identity(len(decimal_values2)).astype(int)]
                # error_dict2 = dict(zip(decimal_values2, error2))
                par2 = np.array([(i + j) % 2 for i in self.parity_matrix_transposed for j in self.parity_matrix_transposed])
                decimal_values2 = np.array([int(''.join(map(str, row)), 2) for row in par2])
                error2 = [(i + j) % 2 for i in np.identity(self.code_bits).astype(int) for j in np.identity(self.code_bits).astype(int)]
                error_dict2 = dict(zip(decimal_values2, error2))

                return {**zero_dict, **error_dict1, **error_dict2}
            case _:
                raise ValueError("max_corr_bits must be between 0 and 2")

    def encode(self, message):
        check_type_np_int_array(message)
        return message @ self.generator_matrix % 2

    def decode(self, codeword):
        check_type_np_int_array(codeword)
        error_syndrome = codeword @ self.parity_matrix_transposed % 2
        print(f'error syndrom: {error_syndrome}')
        error_syndrome_num = int(''.join(map(str, error_syndrome)), 2)
        error_vector = self.syndrome_table.get(error_syndrome_num)
        print(f'error_syndrome_num: {error_syndrome_num}')
        print(f'error_vector: {error_vector}')
        if error_vector is None:
            return None
        message = (codeword ^ error_vector)[self.check_bits:]
        return message, sum(error_vector)

    def __str__(self):
        return f"""Block Codes Information:
            Use bits: {self.use_bits}
            Code bits: {self.code_bits}
            Check bits: {self.check_bits}
            Maximum correction bits: {self.max_corr_bits}
            Generator matrix:\n{self.generator_matrix}
            Part matrix:\n{self.part_matrix}
            Parity matrix:\n{self.parity_matrix}
            Parity matrix transposed:\n{self.parity_matrix_transposed}
            Syndrome Table:\n{self.syndrome_table}"""


def check_type_np_int_array(arr):
    if not (isinstance(arr, np.ndarray) and np.issubdtype(arr.dtype, np.integer)):
        raise (ValueError('Argument be a numpy array of ints'))


def flip_n_bits(arr, n):
    indices = np.random.choice(len(arr), n, replace=False)
    arr[indices] = 1 - arr[indices]
    return arr


def test(message, part_matrix, max_corr_bits):
    bcodes = BlockCodes(part_matrix, max_corr_bits)
    print(bcodes, end='\n\n')

    print(f'message: {message}')
    codeword = bcodes.encode(message)
    print(f"encoded codeword: {codeword}")

    faulty_codeword = flip_n_bits(codeword, 2)
    # faulty_codeword = np.array([1, 0, 1, 0, 1, 1, 1, 1])
    print(f"faulty codeword: {faulty_codeword}")

    if recv:= bcodes.decode(faulty_codeword):
        new_message, corrected_errors = recv
        print(f'received messsage: {new_message}')
        print(f'number of corrected errors: {corrected_errors}')
    else:
        print('Could not correct errors')


def main():
    # test(np.array([0, 1, 1, 0]), np.array([[1, 1, 0], [0, 1, 1], [1, 1, 1], [1, 0, 1]]), 1)  # Test 1
    # test(np.array([1, 1]), np.array([[1, 1, 1, 1, 0, 0], [0, 0, 1, 1, 1, 1]]), 2)  # Test 2
    test(np.array([1, 1, 0]), np.array([[1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 1, 1, 1, 0], [1, 0, 1, 0, 1, 0, 1]]), 2)  # Test 3


if __name__ == '__main__':
    main()
