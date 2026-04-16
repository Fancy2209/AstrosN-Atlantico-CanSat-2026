from machine import UART, Pin
from time import sleep_ms
from utils_no_atlantico import LOW, HIGH, digitalWrite, serialWrite, RadioAdapter, APC220

# Set to true to recieve
RECIEVE = True 

RADIO = "APC"

PIN_TX = Pin(0)
PIN_RX = Pin(1)
PIN_SET = Pin(4, Pin.OUT)

radio: RadioAdapter

if(RADIO == "APC220"):
    radio = APC220(0, 9600, PIN_TX, PIN_RX, 433.450, {PIN_SET: PIN_SET})

    
while True:
    if RECIEVE:
        while radio.available():
            serialWrite(radio.read())
    else:
        radio.println("Hello World!")
    sleep_ms(500)

    
