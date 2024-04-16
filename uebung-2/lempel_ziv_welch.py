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
        dictionary = {char: i for i, char in enumerate(char_list)}
        message = ''

        return message


def main():
    message = 'FISCHERSFRITZFISCHTFRISCHEFISCHE'
    char_list = list(set(message))

    bitstring = LempelZivWelch.encode(message, char_list.copy())
    new_message = LempelZivWelch.decode(bitstring, char_list.copy())

    print(f'original message : "{message}"')
    print(f'encoded bitstring: "{bitstring}"')
    print(f'decoded bitstring: "{new_message}"')


if __name__ == '__main__':
    main()