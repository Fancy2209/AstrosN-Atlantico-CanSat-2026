
from radio import SX1262Adapter
import machine

radio = SX1262Adapter()
uart = machine.UART(0, 9600, tx=machine.Pin(4), rx=machine.Pin(5))

while True:
    uart.write(radio.recieve())
    

    
