
from radio import SX1262Adapter
#import machine
import struct

radio = SX1262Adapter()
#uart = machine.UART(0, 9600, tx=machine.Pin(4), rx=machine.Pin(5))

#while True:
#    pkt = radio.recieve()
#    if pkt:
#        uart.write(pkt)

FMT_STRING_PRIMARY = "<" + "B" + "I" + "fff"
FMT_STRING_SECONDARY = FMT_STRING_PRIMARY + "B" + "fff" + "ffff" + "ff"
while True:
    pkt = radio.recieve()
    if pkt:
        if pkt[0] == 0:
            print(struct.unpack(FMT_STRING_PRIMARY, pkt))

        elif pkt[0] == 1:
            print(struct.unpack(FMT_STRING_SECONDARY, pkt))

    

    
