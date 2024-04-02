from math import log2
from collections import Counter, OrderedDict
import matplotlib as pl



with open("wortliste.txt", 'r') as file:
    words = [line.rstrip() for line in file]

print(words[0])
