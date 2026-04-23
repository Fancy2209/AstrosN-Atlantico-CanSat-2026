import _thread, sdcard, os
from time import sleep_ms, time
from machine import SPI, Pin

sd_buffer_lock = _thread.allocate_lock()
sd_buffer = []
def send_to_ground(radio, msg, no_sd):
    radio.send(msg)

    if not no_sd:
        sd_buffer_lock.acquire()
        sd_buffer.append(msg)
        sd_buffer_lock.release()

def sd_callback():
    while True:
        #print("SD Card Flush")
        sd_buffer_lock.acquire()

        while len(sd_buffer) > 0:
            sdFile.write(sd_buffer.pop(0))

        sdFile.flush()
        sd_buffer_lock.release()
        sleep_ms(1000)

def init_sd():
    global sdFile
    sd = sdcard.SDCard(SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), cs=Pin(17))
    os.mount(sd, "/sd")
    sdFile = open("/sd/" + "data" + str(len(os.listdir("/sd/"))+1) + ".bin", "wb")
    _thread.start_new_thread(sd_callback, [])
