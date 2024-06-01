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
        if crc & (1 << (num_bits + poly_deg(poly) - 1)):
            crc ^= (poly << (num_bits - 1 - i))
        crc <<= 1
    crc >>= 1  # Right shift back to fit the crc to the correct size
    crc = crc & ((1 << poly_deg(poly)) - 1)  # CRC auf die korrekte Länge beschränken
    return crc

def string_to_bits(s):
    bits = []
    for char in s:
        binval = bin(ord(char))[2:]  # Binärdarstellung des Zeichens
        binval = '0' * (8 - len(binval)) + binval  # Manuelles Auffüllen auf 8 Bits (ein Byte)
        bits.extend([int(bit) for bit in binval])  # Jedes Bit zur Liste hinzufügen
    return bits

def bits_to_string(bits):
    return ''.join(chr(bits_to_int(bits[i:i + 8])) for i in range(0, len(bits), 8))

def bits_to_int(bits):
    return int(''.join(str(bit) for bit in bits), 2)

def int_to_bits(i, bit_length=8):
    binval = bin(i)[2:]  # Binärdarstellung des Wertes
    binval = '0' * (bit_length - len(binval)) + binval  # Manuelles Auffüllen auf ganze Bytes
    return [int(bit) for bit in binval]

def bytes_to_bits(by):
    received_bits = []
    for byte in by:
        binval = bin(byte)[2:]
        binval = '0' * (8 - len(binval)) + binval  # Manuelles Auffüllen auf 8 Bits
        received_bits.extend([int(bit) for bit in binval])
    return received_bits

def send_ack(seq_num):
    ack_message = f"{chr(seq_num)}ACK"
    ack_bits = string_to_bits(ack_message)
    ack_int = bits_to_int(ack_bits)
    ack_bitcount = len(ack_bits)
    crc = encode_crc(ack_int, CRC5POLY, ack_bitcount)
    crc_bits = int_to_bits(crc, 8)
    ack_bits.extend(crc_bits)
    bytes_to_send = ack_message + chr(crc)
    uart.write(bytes_to_send)
    print(f"Sent ACK: {ack_message}, CRC: {crc}")

uart = UART(0, 9600)  # UART0: TX (D1), RX (D0)
led = Pin(6, Pin.OUT)
final_received_message = ""

while True:
    # identify()

    uart_input = uart.read()  # Lies alle verfügbaren Bytes
    if uart_input:
        print(f"Received bytes: {list(uart_input)}")  # Debug-Ausgabe der empfangenen Bytes
        received_bits = bytes_to_bits(uart_input)

        received_sequence_number_bits = received_bits[:8]
        received_sequence_number = bits_to_int(received_sequence_number_bits)

        received_message_bits = received_bits[8:-8]
        received_message = bits_to_string(received_message_bits)

        received_crc_bits = received_bits[-8:]
        received_crc = bits_to_int(received_crc_bits)

        crc_validation_data = bits_to_int(received_sequence_number_bits + received_message_bits)
        crc_validation_data_len = len(received_sequence_number_bits) + len(received_message_bits)

        received_bit_blocks = [received_bits[i:i + 8] for i in range(0, len(received_bits), 8)]

        calculated_crc = encode_crc(crc_validation_data, CRC5POLY, crc_validation_data_len)
        calculated_crc_bits = int_to_bits(calculated_crc, 8)

        print(f"Received Message: {uart_input}, Sequence Number: {received_sequence_number}, Message: {received_message}, CRC: {received_crc}")
        print(f"Received CRC: {received_crc}")
        print(f"Calculated CRC: {calculated_crc}")

        if received_crc_bits == calculated_crc_bits:
            print("Received valid message:", uart_input)
            final_received_message += received_message
            send_ack(received_sequence_number)
        else:
            print(f"CRC error for message {received_sequence_number} {uart_input}! Received: {received_crc_bits} Calculated: {calculated_crc_bits}")
        print(final_received_message)
