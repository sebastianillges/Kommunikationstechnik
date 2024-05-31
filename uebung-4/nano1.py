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


def bits_to_string(bits):
    return ''.join(chr(bits_to_int(bits[i:i + 8])) for i in range(0, len(bits), 8))


def bits_to_int(bits):
    return int(''.join(str(bit) for bit in bits), 2)


def int_to_bits(i, bit_length=8):
    binval = bin(i)[2:]  # Binärdarstellung des Wertes
    binval = '0' * (bit_length - len(binval)) + binval  # Manuelles Auffüllen auf ganze Bytes
    return [int(bit) for bit in binval]


uart = UART(0, 9600)  # UART0: TX (D1), RX (D0)
led = Pin(6, Pin.OUT)
sequence_number = 0

while True:
    identify()

    message = "Hi1"
    # print(f"Sending message: {message}")
    message_bits = string_to_bits(str(message))
    # print(f"Message bits: {message_bits}")
    message_int = bits_to_int(message_bits)
    # print(f"Message int: {message_int}")
    message_bitcount = len(message_bits)

    # print(f"Sequence number: {sequence_number}")
    sequence_number_bits = int_to_bits(sequence_number, 8)  # Sicherstellen, dass es 8 Bits sind
    # print(f"Sequence number bits: {sequence_number_bits}")

    sequence_and_message_bits = sequence_number_bits + message_bits
    sequence_and_message_int = bits_to_int(sequence_and_message_bits)
    # print(f"Sequence and message bits: {sequence_and_message_bits}")

    crc = encode_crc(sequence_and_message_int, CRC5POLY, len(sequence_and_message_bits))
    # print(f"CRC: {crc}")
    crc_bits = int_to_bits(crc, 8)  # Sicherstellen, dass CRC in 8 Bits dargestellt wird
    # print(f"CRC bits: {crc_bits}")
    sequence_and_message_bits.extend(crc_bits)
    # print(f"Complete bits to send: {sequence_and_message_bits}")  # Debug-Ausgabe der vollständigen Bits
    bit_blocks = [sequence_and_message_bits[i:i + 8] for i in range(0, len(sequence_and_message_bits), 8)]
    # print(f"Complete bits in 8 blocks: {bit_blocks}")  # Debug-Ausgabe der vollständigen Bits

    bytes_to_send = chr(sequence_number) + str(message) + chr(crc)
    uart.write(bytes_to_send)

    print(
        f"Sent message: {message}, Sequence number: {bit_blocks[0]} = {sequence_number}, Message: {bit_blocks[1:-1]} = {message}, CRC: {bit_blocks[-1]} = {crc}")

    sequence_number = (sequence_number + 1) % 256

    uart_input = uart.read(len(bytes_to_send))  # Anzahl der erwarteten Bytes lesen
    if uart_input:
        uart_message = uart_input
        print(f"Received bytes: {list(uart_message)}")  # Debug-Ausgabe der empfangenen Bytes
        received_bits = []
        for byte in uart_message:
            binval = bin(byte)[2:]
            binval = '0' * (8 - len(binval)) + binval  # Manuelles Auffüllen auf 8 Bits
            received_bits.extend([int(bit) for bit in binval])

        received_sequence_number_bits = received_bits[:8]
        received_sequence_number = bits_to_int(received_sequence_number_bits)

        received_message_bits = received_bits[8:-8]
        received_message = bits_to_string(received_message_bits)

        received_crc_bits = received_bits[-8:]
        received_crc = bits_to_int(received_crc_bits)

        crc_validation_data = bits_to_int(received_sequence_number_bits + received_message_bits)
        crc_validation_data_len = len(received_sequence_number_bits) + len(received_message_bits)

        received_bit_blocks = bit_blocks = [received_bits[i:i + 8] for i in range(0, len(received_bits), 8)]

        calculated_crc = encode_crc(crc_validation_data, CRC5POLY, crc_validation_data_len)
        calculated_crc_bits = int_to_bits(calculated_crc, 8)

        # message_str = ''.join(chr(bits_to_int(received_message_bits[i:i + 8])) for i in range(0, len(received_message_bits), 8))

        print(
            f"Received Message: {uart_message}, Sequence Number:  {received_bit_blocks[0]} = {bits_to_int(received_bit_blocks[0])}, Message: {received_bit_blocks[1:-1]} = {message_str}, CRC: {received_bit_blocks[-1]} = {received_crc}")
        print(f"Received CRC: {received_crc}")
        print(f"Calculated CRC: {calculated_crc}")
        if received_crc_bits == calculated_crc_bits:
            print("Received valid message:", uart_message)
        else:
            print(
                f"CRC error for message {received_sequence_number} {uart_message}! Received: {received_crc_bits} Calculated:  {calculated_crc_bits}")

    time.sleep(5)
