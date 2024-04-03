import math
import matplotlib.pyplot as plt
from sortedcontainers import SortedDict


class Nachrichtenquelle:
    def __init__(self, wort):
        self.wort = wort.lower()
        self.auftrittswahrscheinlichkeiten = SortedDict(self.berechne_auftrittswahrscheinlichkeiten())
        self.informationsgehalt = SortedDict(self.berechne_informationsgehalt())
        self.entropie = self.berechne_entropie()
        self.plot()

    def berechne_auftrittswahrscheinlichkeiten(self):
        wahrscheinlichkeiten = {}
        for zeichen in self.wort:
            if zeichen in wahrscheinlichkeiten:
                wahrscheinlichkeiten[zeichen] += 1
            else:
                wahrscheinlichkeiten[zeichen] = 1
        for zeichen in wahrscheinlichkeiten:
            wahrscheinlichkeiten[zeichen] = round(wahrscheinlichkeiten[zeichen] / len(self.wort), 3)
        print(f"Wahrscheinlichkeiten: {wahrscheinlichkeiten}")
        return wahrscheinlichkeiten

    def berechne_informationsgehalt(self):
        informationsgehalt = {}
        for zeichen, wahrscheinlichkeit in self.auftrittswahrscheinlichkeiten.items():
            informationsgehalt[zeichen] = round(-math.log2(wahrscheinlichkeit), 3)
        print(f"Informationsgehalt: {informationsgehalt}")
        return informationsgehalt

    def berechne_entropie(self):
        entropie = 0
        for wahrscheinlichkeit in self.auftrittswahrscheinlichkeiten.values():
            entropie = round(entropie + wahrscheinlichkeit * -math.log2(wahrscheinlichkeit), 3)
        print(f"Entropie: {entropie}")
        return entropie

    def plot(self):
        plt.plot(self.auftrittswahrscheinlichkeiten.keys(), self.auftrittswahrscheinlichkeiten.values())
        plt.title("Auftrittswahrscheinlichkeiten")
        plt.show()
        plt.plot(self.informationsgehalt.keys(), self.informationsgehalt.values())
        plt.title("Informationsgehalt")
        plt.show()


if __name__ == '__main__':
    # Nachrichtenquelle("Hochschule")
    Nachrichtenquelle(
        "This document describes HTCPCP, a protocol for controlling, monitoring, and diagnosing coffee pots")
