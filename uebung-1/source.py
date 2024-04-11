import math
import matplotlib.pyplot as plt


class Nachrichtenquelle:
    def __init__(self, wort):
        self.wort = wort
        self.auftrittswahrscheinlichkeiten = dict(sorted(self.berechne_auftrittswahrscheinlichkeiten().items(), key=lambda x: x[1], reverse=True))
        self.informationsgehalt = self.berechne_informationsgehalt()
        self.entropie = self.berechne_entropie()

    def berechne_auftrittswahrscheinlichkeiten(self):
        wahrscheinlichkeiten = {}
        for zeichen in self.wort:
            if zeichen in wahrscheinlichkeiten:
                wahrscheinlichkeiten[zeichen] += 1
            else:
                wahrscheinlichkeiten[zeichen] = 1
        for zeichen in wahrscheinlichkeiten:
            wahrscheinlichkeiten[zeichen] = round(wahrscheinlichkeiten[zeichen] / len(self.wort), 3)
        return wahrscheinlichkeiten

    def berechne_informationsgehalt(self):
        informationsgehalt = {}
        for zeichen, wahrscheinlichkeit in self.auftrittswahrscheinlichkeiten.items():
            informationsgehalt[zeichen] = round(-math.log2(wahrscheinlichkeit), 3)
        return informationsgehalt

    def berechne_entropie(self):
        entropie = 0
        for wahrscheinlichkeit in self.auftrittswahrscheinlichkeiten.values():
            entropie = round(entropie + wahrscheinlichkeit * -math.log2(wahrscheinlichkeit), 3)
        return entropie

    def plot(self):
        plt.plot(self.auftrittswahrscheinlichkeiten.keys(), self.auftrittswahrscheinlichkeiten.values())
        plt.title("Auftrittswahrscheinlichkeiten")
        plt.show()
        plt.plot(self.informationsgehalt.keys(), self.informationsgehalt.values())
        plt.title("Informationsgehalt")
        plt.show()


if __name__ == '__main__':
    # nachrichtenquelle = Nachrichtenquelle("Hochschule")
    nachrichtenquelle = Nachrichtenquelle(
        "This document describes HTCPCP, a protocol for controlling, monitoring, and diagnosing coffee pots")

    print(f'Wahrscheinlichkeiten: {nachrichtenquelle.auftrittswahrscheinlichkeiten}')
    print(f'Informationsgehalt: {nachrichtenquelle.informationsgehalt}')
    print(f'Entropie: {nachrichtenquelle.entropie}')
    # nachrichtenquelle.plot()
