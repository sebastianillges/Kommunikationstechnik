from arithmetic_compressor.models import StaticModel
from arithmetic_compressor import AECompressor
from random import choices
import matplotlib.pyplot as plt

from source import Nachrichtenquelle
from shannon import shannon_fano


def a2():
    print("Test RFC2324")
    data = open("rfc2324.txt", "r").read().lower()

    model = StaticModel(Nachrichtenquelle(data).auftrittswahrscheinlichkeiten)
    coder = AECompressor(model)

    ac_compressed = coder.compress(data)
    # print(ac_compressed)

    decoded = coder.decompress(ac_compressed, len(data))
    # print(decoded)

    code = shannon_fano(Nachrichtenquelle(data))
    sh_compressed = []
    for letter in data:
        for num in code[letter]:
            sh_compressed.append(int(num))
    # print(sh_compressed)

    diff = len(sh_compressed) / len(ac_compressed)
    signed_diff_percent = (diff - 1) * 100
    sign = '+' if signed_diff_percent >= 0 else '-'

    print("Results:")
    print(f"Arithmetic Compressor: Code length = {len(ac_compressed)}")
    print(f"Shannon: Code length = {len(sh_compressed)} ({sign}{round(abs(signed_diff_percent), 2)}%)")


def a3():
    print("Test Random RFC 2324")
    ac_lengths = []
    sh_lengths = []

    for i in range(10):
        data = str(choices([char for char in open("rfc2324.txt", "r").read().lower() if char.isalpha()], k=1000))

        model = StaticModel(Nachrichtenquelle(data).auftrittswahrscheinlichkeiten)
        coder = AECompressor(model)

        ac_compressed = coder.compress(data)
        ac_lengths.append(len(ac_compressed))
        # print(ac_compressed)

        decoded = coder.decompress(ac_compressed, len(data))
        # print(decoded)

        code = shannon_fano(Nachrichtenquelle(data))
        sh_compressed = []
        for letter in data:
            for num in code[letter]:
                sh_compressed.append(int(num))
        # print(sh_compressed)
        sh_lengths.append(len(sh_compressed))

        diff = len(sh_compressed) / len(ac_compressed)
        signed_diff_percent = (diff - 1) * 100
        sign = '+' if signed_diff_percent >= 0 else '-'

        print("Results:")
        print(f"Arithmetic Compressor: Code length = {len(ac_compressed)}")
        print(f"Shannon: Code length = {len(sh_compressed)} ({sign}{round(abs(signed_diff_percent), 2)}%)")

    plt.bar(["AC", "SH"], [sum(ac_lengths) / 10, sum(sh_lengths) / 10])
    plt.show()


if __name__ == '__main__':
    a2()
    a3()
