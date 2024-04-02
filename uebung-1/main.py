from math import log2
from collections import Counter, OrderedDict
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
