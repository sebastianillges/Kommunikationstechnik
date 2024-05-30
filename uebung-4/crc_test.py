CRC5POLY = 0b110101  # CRC-5 Polynom
print(f"POLY = {CRC5POLY:b}")

# nutzdaten = [1, 0, 0, 0, 1, 1, 0, 0]
nutzdaten = 0b11011
bitcount = len(bin(nutzdaten)) - 2  # Anzahl der Bits in nutzdaten

def poly_deg(poly):
    return len(bin(poly)) - 3

def calculate_crc(data, poly, num_bits):
    # Initialisierung des CRC-Registers mit Nullen
    crc = data << (poly_deg(poly))  # Data left-shifted by degree of the polynomial
    # print(f"{crc:b}")
    for i in range(num_bits):
        # Wenn das oberste Bit 1 ist, XOR mit dem Polynom
        if crc & (1 << (num_bits + poly_deg(poly) - 1)):
            # print(f"{(poly << (num_bits - 1 - i)):b}")
            crc ^= (poly << (num_bits - 1 - i))
            # print(f"{crc:b}")
        else:
            crc = crc << 1
    # Rückgabe des CRC-Wertes
    crc = crc & ((1 << poly_deg(poly)) - 1)  # CRC auf die korrekte Länge beschränken
    return crc

def check_crc(data, poly, num_bits, received_crc):
    # Daten mit dem empfangenen CRC-Wert kombinieren
    combined_data = (data << poly_deg(poly)) | received_crc
    calculated_crc = calculate_crc(data, poly, num_bits)
    return calculated_crc == received_crc

# Kodierung der Nutzdaten mit CRC5
crc = calculate_crc(nutzdaten, CRC5POLY, bitcount)
print(f"Nutzdaten = {nutzdaten:b}")
print(f"CRC = {crc:05b}")

# Überprüfung der empfangenen Daten
is_valid = check_crc(nutzdaten, CRC5POLY, bitcount, crc)
print(f"Is the received data valid? {is_valid}")
