import sys
from machine import UART, Pin
from enum import Enum
from abc import ABC, abstractmethod
from time import sleep_ms

LOW = 0
HIGH = 1
    
def digitalWrite(pin, val):
    pin.value(val)


def serialWrite(s):
    sys.stdout.buffer.write(s)

class RadioAdapter(ABC):
    @abstractmethod
    def __init__(self, id, baud, tx, rx, freq):
        pass

    @abstractmethod
    def println(self, msg):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def available(self):
        pass

class APC220(RadioAdapter):

    def __init__(self, id, baud, tx, rx, freq, additionalData = None):
        if additionalData != None:
            digitalWrite(additionalData.PIN_SET, HIGH)
            self.uart = UART(id, baud)
            self.uart.init(baud, bits=8, parity=None, stop=1, tx=tx, rx=rx)
        
            digitalWrite(additionalData.PIN_SET, LOW)
            sleep_ms(10)
            self.println("WR " + freq*100 + " 3 9 3 0")
            sleep_ms(10)
            
            while self.available():
                serialWrite(self.read())
            
            digitalWrite(additionalData.PIN_SET, HIGH)
            sleep_ms(200)

    def println(self, msg):
        self.uart.write((msg + "\r\n").encode())
        self.uart.flush()

    def read(self):
        self.uart.read()

    def available(self):
        return self.uart.any()

    