import sys
from machine import Pin

LOW = 0
HIGH = 1
    
def digitalWrite(pin, val):
    if isinstance(pin, int):
        Pin(pin).value(val)
    elif isinstance(pin, Pin):
        pin.value(val)

def serialWrite(s):
    sys.stdout.buffer.write(s)
