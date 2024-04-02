from math import log2
import matplotlib.pyplot as plt

with open("wortliste.txt", 'r') as file:
    words = [line.rstrip() for line in file]
    seven_letter_words = [word for word in words if len(word) == 7]
xylofon = "Xylofon"


def a1_1():
    print("Aufgabe 1.1")
    lengths = []
    results = []

    for length in range(2, len(max(words, key=len))):
        counter = 0
        lengths.append(length)
        for word in words:
            if len(word) == length:
                counter += 1
        results.append(log2(len(words) / counter))
        # print(f"{length}: {log2(len(words) / counter)}")

    plt.plot(lengths, results)
    plt.xlabel("Wortlaenge")
    plt.ylabel("Informationsgehalt")
    plt.title("Aufgabe 1.1")
    plt.show()


def a1_2():
    print("Aufgabe 1.2")
    for i, letter in enumerate(xylofon):
        findings = 0
        for word in seven_letter_words:
            if word[i] == letter:
                findings += 1
        plt.bar(f"{i}, {letter}", log2(len(seven_letter_words) / findings))
    plt.title("Aufgabe 1.2")
    plt.show()


def a1_3():
    last = len(seven_letter_words)
    for i, letter in enumerate(xylofon):
        findings = 0
        for word in seven_letter_words:
            if word.startswith(xylofon[0:i + 1]):
                findings += 1
        print(
            f"Anzahl Woerter der Laenge 7, die mit {xylofon[0:i + 1]} beginnen: {findings}, Informationsgehalt = {log2(last / findings)}")
        plt.bar(f"{i}, {letter}", log2(last / findings))
        last = findings
    plt.title("Aufgabe 1.3 Vorwaerts")
    plt.show()

    last = len(seven_letter_words)
    for i, letter in enumerate(reversed(xylofon)):
        findings = 0
        for word in seven_letter_words:
            if word.endswith(xylofon[len(xylofon) - i - 1:]):
                findings += 1
        print(
            f"Anzahl Woerter der Laenge 7, die mit {xylofon[len(xylofon) - i - 1:]} enden: {findings}, Informationsgehalt = {log2(last / findings)}")
        plt.bar(f"{i}, {letter}", log2(last / findings))
        last = findings
    plt.title("Aufgabe 1.3 Rueckwaerts")
    plt.show()


if __name__ == '__main__':
    # a1_1()
    # a1_2()
    a1_3()
