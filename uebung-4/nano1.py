from machine import UART, Pin
import time

def identify():
  led.on()
  time.sleep_ms(100)
  led.off()

uart = UART(0, 9600)                         # init with given baudrate
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

led = Pin(6, Pin.OUT)

while True:
    identify()
    uart.write("Hello from Nano 1\n")
    uart_input = uart.readline()
    print(f"Received: {uart_input}")
    time.sleep_ms(1000)