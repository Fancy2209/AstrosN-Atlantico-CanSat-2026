from sx1262 import SX1262

FREQ  = 433.450
BW    = 250.0 
SF    = 9
CR    = 8
POWER = 20

class SX1262Adapter():

    def __init__(self):
        self.sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)
        self.sx.begin(freq=FREQ, bw=BW, sf=SF, cr=CR, syncWord=0x12,
             power=POWER, currentLimit=60.0, preambleLength=8,
             implicit=False, implicitLen=0xFF,
             crcOn=True, txIq=False, rxIq=False,
             tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)
        
    def send(self, msg):
        self.sx.send(msg)

    def print(self, msg):
        self.send(msg.encode())

    def recieve(self, len=0, timeout_en=False, timeout_ms=0):
        return self.sx.recv(len, timeout_en, timeout_ms)
    
    def println(self, msg):
        self.print(msg)
        self.send("\r\n".encode())

    def read(self):
        return self.sx.recv()
    
    def getRssi(self):
        return self.sx.getRSSI()