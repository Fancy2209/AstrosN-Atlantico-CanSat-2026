
from radio import SX1262Adapter
import machine
import struct

radio = SX1262Adapter()
uart = machine.UART(0, 9600, tx=machine.Pin(0), rx=machine.Pin(1))

#while True:
#    pkt = radio.recieve()
#    if pkt:
#        uart.write(pkt)

def printAndUart(msg):
    print(msg, end="")
    uart.write(msg)

FMT_STRING_PRIMARY = "<" + "B" + "I" + "fff"
FMT_STRING_SECONDARY = FMT_STRING_PRIMARY + "B" + "fff" + "ffff"
while True:
    try:
        print("HIII")
        pkt = radio.recieve()
        print(f"pkt: {pkt}")
        type = pkt[0][:1]
        if pkt and pkt[0] and len(pkt[0]) >= struct.calcsize(FMT_STRING_PRIMARY):
            if type == b'\x00':
                printAndUart(str(list(struct.unpack(FMT_STRING_PRIMARY, pkt[0])))
                             .replace("[", "")
                             .replace("]", "") 
                             + "\r\n"
                )

            elif type == b'\x01':
                printAndUart(str(list(struct.unpack(FMT_STRING_SECONDARY, pkt[0]))).replace("[", "").replace("]", "") + "\r\n")
    except Exception as ex:
        print(f"Died {ex}")
        if isinstance(ex, KeyboardInterrupt):
            break

    

    
