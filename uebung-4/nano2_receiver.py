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
    ack_message = bytearray([seq_num]) + b'ACK'
    ack_bits = string_to_bits(ack_message.decode('latin-1'))  # Use 'latin-1' to decode bytearray
    ack_int = bits_to_int(ack_bits)
    ack_bitcount = len(ack_bits)
    crc = encode_crc(ack_int, CRC5POLY, ack_bitcount)
    crc_bits = int_to_bits(crc, 8)
    ack_bits.extend(crc_bits)
    bytes_to_send = ack_message + bytearray([crc])
    uart.write(bytes_to_send)
    print(f"Sent ACK: {seq_num}{ack_message}, CRC: {crc}")

def evaluate_message(original, modified):
    extra_repeats = 0
    wrong_chars = 0
    total_errors = 0

    original_index = 0
    modified_index = 0

    while original_index < len(original) and modified_index < len(modified):
        if original[original_index] == modified[modified_index]:
            original_index += 1
            modified_index += 1
        elif modified_index > 0 and modified[modified_index] == modified[modified_index - 1]:
            extra_repeats += 1
            modified_index += 1
        else:
            wrong_chars += 1
            modified_index += 1

    total_errors = extra_repeats + wrong_chars

    # Remaining characters in modified string are considered wrong characters
    if modified_index < len(modified):
        wrong_chars += len(modified) - modified_index
        total_errors = extra_repeats + wrong_chars

    return extra_repeats, wrong_chars, total_errors

uart = UART(0, 9600)  # UART0: TX (D1), RX (D0)
led = Pin(6, Pin.OUT)
timeout = 5
time_start = time.time()
expected_message = "This document specifies a Hyper Text Coffee Pot Control Protocol\
   (HTCPCP), which permits the full request and responses necessary to\
   control all devices capable of making the popular caffeinated hot\
   beverages.\
\
   HTTP 1.1 ([RFC2068]) permits the transfer of web objects from origin\
   servers to clients."

final_received_message = ""

while True:
    identify()
    if time.time() - time_start > timeout:
        print("Timeout!")
        break

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
            time_start = time.time()
        else:
            print(f"CRC error for message {received_sequence_number} {uart_input}! Received: {received_crc_bits} Calculated: {calculated_crc_bits}")
            time_start = time.time()
        print(final_received_message)

extra_repeats, wrong_chars, total_errors = evaluate_message(expected_message, final_received_message)
print(f"Anzahl überflüssiger Wiederholungen: {extra_repeats}")
print(f"Anzahl falscher Zeichen: {wrong_chars}")
print(f"Anzahl gesamt Fehler: {total_errors}")
