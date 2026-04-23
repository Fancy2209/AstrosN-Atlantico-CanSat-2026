import _thread, sdcard, os, struct
from time import sleep_ms, time
from machine import SPI, Pin
import io

# TODO: Should I add an header?
FMT_STRING_PRIMARY = "<" + "B" + "I" + "fff"
FMT_STRING_SECONDARY = FMT_STRING_PRIMARY + "B" + "fff" + "ffff"
msg_type_to_fmt = [FMT_STRING_PRIMARY, FMT_STRING_SECONDARY]

sd_buffer_lock = _thread.allocate_lock()
sd_buffer: list[str] = []
def send_to_ground(radio, msg, no_sd, msg_type):
    radio.send(msg)

    if not no_sd and sdOpen:
        sd_buffer_lock.acquire()
        sd_buffer.append(
            str(
                list(
                    struct.unpack(msg_type_to_fmt[msg_type], msg)
                )
            ).replace("[", "").replace("]", "")
        )
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
    global sdFile, sdOpen
    sd = sdcard.SDCard(SPI(0, sck=Pin(18), mosi=Pin(19), miso=Pin(16)), cs=Pin(17))
    # SCK:  Pino 24
    # MOSI: Pino 25
    # MISO: Pino 21
    # CS:   Pino 22
    os.mount(sd, "/sd")
    sdFile = open("/sd/" + "data" + str(len(os.listdir("/sd/"))+1) + ".csv", "w+")
    sdOpen = True
    _thread.start_new_thread(sd_callback, [])

def dump_sd_and_close():
    print("SD DUMP")
    while len(sd_buffer) > 0: sleep_ms(50)
    print(sdFile.readlines())
    sdOpen = False
    print(sdFile.close())