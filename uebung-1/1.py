from math import log2
import matplotlib.pyplot as plt


with open("wortliste.txt", 'r') as file:
    words = [line.rstrip() for line in file]

lengths = []
results = []

for length in range(2, len(max(words, key=len))):
    counter = 0
    lengths.append(length)
    for word in words:
        if len(word) == length:
            counter += 1
    results.append(log2(len(words) / counter))
    print(f"{length}: {log2(len(words) / counter)}")

plt.plot(lengths, results)
plt.xlabel("Wordlength")
plt.ylabel("Informationsgehalt")
plt.show()

xylofon = "Xylofon"

words_with_len_seven = []
for word in words:
    if len(word) == 7:
        words_with_len_seven.append(word)

for i, letter in enumerate(xylofon):
    findings = 0
    for word in words_with_len_seven:
        if word[i] == letter:
            findings += 1
    plt.bar(f"{i}, {letter}", log2(len(words_with_len_seven) / findings))
plt.show()

results = []
last = len(words_with_len_seven)
for i, letter in enumerate(xylofon):
    findings = 0
    for word in words_with_len_seven:
        if word.startswith(xylofon[0:i]):
            findings += 1
    plt.bar(f"{i}, {letter}", log2(last / findings))
    last = findings
plt.show()


    # filter(str.startswith, words_with_len_seven, )