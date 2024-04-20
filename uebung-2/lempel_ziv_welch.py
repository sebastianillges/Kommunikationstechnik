# lempel_ziv_welch.py

class LempelZivWelch:
    @staticmethod
    def encode(message, char_list):
        bitstring = []
        pattern = ''

        for char in message:
            if pattern + char in char_list:
                pattern = pattern + char
            else:
                char_list.append(pattern + char)
                bitstring.append(char_list.index(pattern))
                pattern = char

        if pattern:
            bitstring.append(char_list.index(pattern))
        return bitstring

    @staticmethod
    def decode(bitstring, char_list):
        dictionary = {i: char for i, char in enumerate(char_list)}
        message = ''
        last = bitstring[0]
        message += dictionary[last]
        for char in bitstring[1:]:
            if char in dictionary.keys():
                dictionary[len(dictionary)] = dictionary[last] + dictionary[char][:1]
            else:
                dictionary[len(dictionary)] = dictionary[last] + dictionary[last][:1]
            message += dictionary[char]
            last = char
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


def test(message):
    char_list = list(set(message))

    bitstring = LempelZivWelch.encode(message, char_list.copy())
    new_message = LempelZivWelch.decode(bitstring, char_list.copy())

    print(f'original message : "{message}"')
    print(f'encoded bitstring: "{bitstring}"')
    print(f'decoded bitstring: "{new_message}"')
    print(f'diff: {char_diffs(message, new_message)}')


def main():
    test("FISCHERSFRITZFISCHTFRISCHEFISCHE")
    test(open("rfc2324.txt", "r").read())


if __name__ == '__main__':
    main()
