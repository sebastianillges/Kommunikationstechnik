from machine import UART, Pin
import time

CRC5POLY = 0b110101  # CRC-5 Polynom


def identify():
    led.on()
    time.sleep_ms(100)
    led.off()


def poly_deg(poly):
    return len(bin(poly)) - 3


def encode_crc(data, poly, num_bits):
    crc = data << (poly_deg(poly))  # Data left-shifted by degree of the polynomial
    for i in range(num_bits):
        if (crc & (1 << (num_bits + poly_deg(poly) - 1))):
            crc ^= (poly << (num_bits - 1 - i))
        else:
            crc <<= 1
    crc = crc & ((1 << poly_deg(poly)) - 1)  # CRC auf die korrekte Länge beschränken
    return crc


def string_to_bits(s):
    bits = []
    for char in s:
        binval = bin(ord(char))[2:]  # Binärdarstellung des Zeichens
        binval = '0' * (8 - len(binval)) + binval  # Manuelles Auffüllen auf 8 Bits (ein Byte)
        bits.extend([int(bit) for bit in binval])  # Jedes Bit zur Liste hinzufügen
    return bits


def bits_to_bytes(bits):
    byte_arr = bytearray()
    for b in range(0, len(bits), 8):
        byte = bits[b:b + 8]
        byte_str = ''.join(str(bit) for bit in byte)
        byte_arr.append(int(byte_str, 2))
    return bytes(byte_arr)


def bits_to_int(bits):
    return int(''.join(str(bit) for bit in bits), 2)


uart = UART(0, 9600)  # UART0: TX (D1), RX (D0)
led = Pin(6, Pin.OUT)

while True:
    identify()
    message = "1"
    bit_list = string_to_bits(message)
    nutzdaten = bits_to_int(bit_list)
    bitcount = len(bit_list)

    crc = encode_crc(nutzdaten, CRC5POLY, bitcount)
    crc_bits = [int(bit) for bit in bin(crc)[2:]]
    crc_bits = [0] * (poly_deg(CRC5POLY) - len(crc_bits)) + crc_bits  # Manuelles Auffüllen auf die richtige Länge
    bit_list.extend(crc_bits)
    uart.write(bits_to_bytes(bit_list))

    print(f"Sent message: {message}, {bit_list} {crc_bits}")

    uart_input = uart.readline()
    if uart_input:
        received_message = uart_input
        received_bits = []
        for byte in received_message:
            binval = bin(byte)[2:]
            binval = '0' * (8 - len(binval)) + binval  # Manuelles Auffüllen auf 8 Bits
            received_bits.extend([int(bit) for bit in binval])

        received_crc = bits_to_int(received_bits[-poly_deg(CRC5POLY):])
        message_bits = received_bits[:-poly_deg(CRC5POLY)]

        nutzdaten = bits_to_int(message_bits)
        bitcount = len(message_bits)

        calculated_crc = encode_crc(nutzdaten, CRC5POLY, bitcount)

        message_str = ''.join(chr(bits_to_int(message_bits[i:i + 8])) for i in range(0, len(message_bits), 8))

        print(f"Received bits: {message_bits} {received_bits[-poly_deg(CRC5POLY):]}")

        if received_crc == calculated_crc:
            print("Received valid message:", message_str)
        else:
            print("CRC error for message", message_str, "! Received:", bin(received_crc), "Calculated:",
                  bin(calculated_crc))

    time.sleep(5)
