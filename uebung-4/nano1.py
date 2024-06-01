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

def is_ack(bits):
    if len(bits) < 32:
        return False
    received_ack_bits = bits[8:32]  # 3*8 = 24 bits for "ACK"
    received_ack = bits_to_string(received_ack_bits)
    return received_ack == "ACK"

def send_message(message, sequence_number):
    message_bits = string_to_bits(str(message))
    message_int = bits_to_int(message_bits)
    message_bitcount = len(message_bits)

    sequence_number_bits = int_to_bits(sequence_number, 8)
    sequence_and_message_bits = sequence_number_bits + message_bits
    sequence_and_message_int = bits_to_int(sequence_and_message_bits)

    crc = encode_crc(sequence_and_message_int, CRC5POLY, len(sequence_and_message_bits))
    crc_bits = int_to_bits(crc, 8)
    sequence_and_message_bits.extend(crc_bits)

    bytes_to_send = chr(sequence_number) + str(message) + chr(crc)
    uart.write(bytes_to_send)

    print(f"Sent message: {message}, Sequence number: {sequence_number}, CRC: {crc}")
    return len(bytes_to_send)

def receive_ack():
    uart_inp = uart.read(4)  # Anzahl der erwarteten Bytes für ACK
    if uart_inp:
        rec_bits = bytes_to_bits(uart_inp)
        if is_ack(rec_bits):
            rec_sequence_number_bits = rec_bits[:8]
            rec_sequence_number = bits_to_int(rec_sequence_number_bits)
            return rec_sequence_number
    return None

uart = UART(0, 9600)  # UART0: TX (D1), RX (D0)
led = Pin(6, Pin.OUT)
sequence_number = 0
received_ack = False
timeout = 5
time_start = time.time()

# message = "Hello from Nano 1!"
message = "test"
# message = "This document specifies a Hyper Text Coffee Pot Control Protocol\
#    (HTCPCP), which permits the full request and responses necessary to\
#    control all devices capable of making the popular caffeinated hot\
#    beverages.\
# \
#    HTTP 1.1 ([RFC2068]) permits the transfer of web objects from origin\
#    servers to clients. The web is world-wide.  HTCPCP is based on HTTP.\
#    This is because HTTP is everywhere. It could not be so pervasive\
#    without being good. Therefore, HTTP is good. If you want good coffee,\
#    HTCPCP needs to be good. To make HTCPCP good, it is good to base\
#    HTCPCP on HTTP.\
# \
#    Future versions of this protocol may include extensions for espresso\
#    machines and similar devices."
send_message(message[sequence_number], sequence_number)

while True:
    # identify()

    if sequence_number == len(message):
        break

    if received_ack:
        time_start = time.time()
        sequence_number += 1
        if sequence_number < len(message):
            send_message(message[sequence_number], sequence_number)
        received_ack = False
    else:
        if time.time() - time_start > timeout:
            print("Timeout! Resending message.")
            send_message(message[sequence_number], sequence_number)
            time_start = time.time()

    uart_input = uart.read()  # Anzahl der erwarteten Bytes lesen
    if uart_input:
        received_bits = bytes_to_bits(uart_input)

        maybe_ack = receive_ack()
        if maybe_ack is not None:
            if maybe_ack == sequence_number:
                print(f"Received valid ACK for sequence number: {sequence_number}")
                received_ack = True
            else:
                print(f"Received wrong ACK: {maybe_ack}! Expected: {sequence_number}")
            continue

        received_sequence_number_bits = received_bits[:8]
        received_sequence_number = bits_to_int(received_sequence_number_bits)

        received_message_bits = received_bits[8:-8]
        received_message = bits_to_string(received_message_bits)

        message_str = bits_to_string(received_message_bits)

        received_crc_bits = received_bits[-8:]
        received_crc = bits_to_int(received_crc_bits)

        crc_validation_data = bits_to_int(received_sequence_number_bits + received_message_bits)
        crc_validation_data_len = len(received_sequence_number_bits) + len(received_message_bits)

        received_bit_blocks = [received_bits[i:i + 8] for i in range(0, len(received_bits), 8)]

        calculated_crc = encode_crc(crc_validation_data, CRC5POLY, crc_validation_data_len)
        calculated_crc_bits = int_to_bits(calculated_crc, 8)

        print(f"Received Message: {uart_input}, Sequence Number: {received_sequence_number}, Message: {message_str}, CRC: {received_crc}")
        if received_crc_bits == calculated_crc_bits:
            if message_str == "ACK":
                if received_sequence_number == sequence_number:
                    received_ack = True
                    print("Received valid ACK:", uart_input)
                else:
                    sequence_number = received_sequence_number
                    print("Received ACK for wrong sequence number! Resending message.")
            else:
                print("Received valid message:", uart_input)
        else:
            print(f"CRC error for message {received_sequence_number} {uart_input}! Received: {received_crc_bits} Calculated: {calculated_crc_bits}")
