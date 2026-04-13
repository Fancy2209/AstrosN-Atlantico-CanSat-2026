from machine import Pin, SPI
import sdcard
import os

# Configura o barramento SPI0
spi = SPI(0, baudrate=1000000, polarity=0, phase=0, 
          sck=Pin(18), mosi=Pin(19), miso=Pin(16))

# Configura o pino CS
cs = Pin(17, Pin.OUT)

# Inicializa o cartão SD
sd = sdcard.SDCard(spi, cs)
os.mount(sd, "/sd")

print("Arquivos no cartão:", os.listdir("/sd"))