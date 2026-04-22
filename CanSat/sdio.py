import _thread, sdcard, os
from time import sleep_ms, time
from machine import SPI, Pin

sd_buffer_lock = _thread.allocate_lock()
sd_buffer = []
def sendToGround(radio, msg):
    radio.send(msg)

    sd_buffer_lock.acquire()
    sd_buffer.append(msg)
    sd_buffer_lock.release()

def sdCallback():
    while True:
        print("SD Card Flush")
        sd_buffer_lock.acquire()

        while len(sd_buffer) > 0:
            sdFile.write(sd_buffer.pop(0))

        sdFile.flush()
        sd_buffer_lock.release()
        sleep_ms(1000)

def initSd():
    global sdFile
    sdFile = open("/sd/" + str(time()) + ".bin", "wb")
    sd = sdcard.SDCard(SPI(1, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), cs=Pin(17))
    os.mount(sd, "/sd")

