# entropy.py

from source import Nachrichtenquelle
from shannon import shannon_fano
from statistics import mean
from math import log2


class Entropy:
    def __init__(self, coding_func, source):
        self.coding_func = coding_func
        self.source = source
        self.codes = coding_func(source)

        self.source_av_char_length = mean([len(x) for x in self.codes.values()])
        self.source_redundancy = self.source_av_char_length - self.source.entropie


    def encode(self, word):
        code = ''
        char_length = 0
        for letter in word:
            if val := self.codes.get(letter):
                code += val
                char_length += len(val)
            else:
                return '', 0.0, 0.0

        av_char_length = char_length / len(word)

        tmp = Nachrichtenquelle(word)
        redundancy = av_char_length - tmp.entropie

        return code, av_char_length, redundancy


    def decode(self, code):
        word = ''

        return word


def main():
    source = Nachrichtenquelle('HOCHSCHULE')
    entropy = Entropy(shannon_fano, source)

    print(entropy.encode('HOCHSCHULE'))
    print(f'"HHHHH": {entropy.encode('HHHHH')}')
    print(f'"EEEEE": {entropy.encode('EEEEE')}')


if __name__ == '__main__':
    main()
