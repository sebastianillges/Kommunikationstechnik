class LempelZiv:
    def __init__(self, ref_bits, len_bits):
        self.ref_bits = ref_bits
        self.len_bits = len_bits

    def encode(self, message):
        char_set = sorted(set(message))
        char_dict = {char: format(index, '0' + str(len(char_set).bit_length()) + 'b') for index, char in enumerate(char_set)}
        encoded_message = ''
        pos = 0
        while pos < len(message):
            max_match_len = 0
            max_match_pos = 0
            for i in range(1, min(self.len_bits, len(message) - pos) + 1):
                sub_message = message[pos:pos + i]
                match_pos = message.rfind(sub_message, 0, pos)
                if match_pos != -1 and pos - match_pos <= 2**self.ref_bits - 1:
                    max_match_len = i
                    max_match_pos = pos - match_pos
            if max_match_len > 0:
                encoded_message += '1' + format(max_match_pos, '0' + str(self.ref_bits) + 'b') + format(max_match_len - 1, '0' + str(self.len_bits) + 'b')
                pos += max_match_len
            else:
                encoded_message += '0' + char_dict[message[pos]]
                pos += 1
        return encoded_message, char_dict

    def decode(self, bitstring, char_dict):
        message = ''
        pos = 0
        while pos < len(bitstring):
            if bitstring[pos] == '0':
                message += next(key for key, value in char_dict.items() if value == bitstring[pos + 1:pos + 1 + len(char_dict[key])])
                pos += 1 + len(char_dict[message[-1]])
            else:
                ref_pos = int(bitstring[pos + 1:pos + 1 + self.ref_bits], 2)
                ref_len = int(bitstring[pos + 1 + self.ref_bits:pos + 1 + self.ref_bits + self.len_bits], 2) + 1
                message += message[-ref_pos:][:ref_len]
                pos += 1 + self.ref_bits + self.len_bits
        return message


def char_diffs(str1, str2):
    diff = []
    for i in range(min(len(str1), len(str2))):
        if str1[i] != str2[i]:
            diff.append((i, str1[i], str2[i]))
    if len(str1) != len(str2):
        longer, shorter = (str1, str2) if len(str1) > len(str2) else (str2, str1)
        for i in range(len(shorter), len(longer)):
            diff.append((i, longer[i], ''))
    return diff


def find_optimal_combination(message):
    min_size = float('inf')
    optimal_ref_bits = 0
    optimal_len_bits = 0

    for ref_bits in range(1, len(message)):
        for len_bits in range(1, len(message)):
            lz = LempelZiv(ref_bits=ref_bits, len_bits=len_bits)
            encoded_message, _ = lz.encode(message)
            compressed_size = len(encoded_message)
            if compressed_size < min_size:
                min_size = compressed_size
                optimal_ref_bits = ref_bits
                optimal_len_bits = len_bits

    print("Optimal ref_bits:", optimal_ref_bits)
    print("Optimal len_bits:", optimal_len_bits)

def find_optimal_combination_speedup(message):
    min_size = float('inf')
    optimal_ref_bits = 0
    optimal_len_bits = 0

    for ref_bits in range(1, len(message)):
        for len_bits in range(1, len(message)):
            lz = LempelZiv(ref_bits=ref_bits, len_bits=len_bits)
            encoded_message, _ = lz.encode(message)
            compressed_size = len(encoded_message)
            if compressed_size < min_size:
                min_size = compressed_size
                optimal_ref_bits = ref_bits
                optimal_len_bits = len_bits


    print("Optimal ref_bits:", optimal_ref_bits)
    print("Optimal len_bits:", optimal_len_bits)


def test(message):
    lz = LempelZiv(ref_bits=3, len_bits=2)

    bitstring, char_list = lz.encode(message)
    new_message = lz.decode(bitstring, char_list)

    print(f'original message : "{message}"')
    print(f'encoded bitstring: "{bitstring}"')
    print(f'decoded bitstring: "{new_message}"')
    print(f'diff: {char_diffs(message, new_message)}')
    return bitstring


def main():
    # message = "FISCHERSFRITZFISCHTFRISCHEFISCHE"
    message = open("rfc2324.txt", "r").read()
    # test(message)

    find_optimal_combination_speedup(message)


if __name__ == '__main__':
    main()
