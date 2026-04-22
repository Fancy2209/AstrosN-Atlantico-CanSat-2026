
from radio import SX1262Adapter
from sdio import initSd, sendToGround
from sensors import Sensors, STABILITY_UNKNOWN, STABILITY_STATIONARY, STABILITY_ON_TABLE
from time import ticks_ms, ticks_diff
import machine
import struct

PACKET_KIND_PRIMARY   = 0
PACKET_KIND_SECONDARY = 1

FMT_STRING_PRIMARY = "B" + "I" + "fff"
FMT_STRING_SECONDARY = FMT_STRING_PRIMARY + "B" + "fff" + "ffff" + "ff"

#machine.RTC().datetime((2026, 4, 22, 21, 48, 0, 0))
initSd()
radio = SX1262Adapter()
sensors = Sensors()
last_stability: int = STABILITY_UNKNOWN

start_time = last_time = last_secondary = ticks_ms()

while True:
    SHOULD_CALM_DOWN = (last_stability == STABILITY_STATIONARY or last_stability == STABILITY_ON_TABLE)
    time_elapsed_secondary = ticks_diff(ticks_ms(), last_secondary)
    time_elapsed = ticks_diff(ticks_ms(), last_time)
    time = ticks_diff(ticks_ms(), start_time)

    sensors.update()

    msg_type = PACKET_KIND_PRIMARY
    bme_vals = sensors.read_bme()

    if time_elapsed_secondary >= 1000 and not SHOULD_CALM_DOWN:
        msg_type = PACKET_KIND_SECONDARY
        bno_vals = sensors.read_bno()
        gps_vals = sensors.read_gps()
        sendToGround(radio, struct.pack(FMT_STRING_SECONDARY, msg_type, time, *bme_vals, *bno_vals, *gps_vals))
        last_stability = bno_vals[0]

    # we check for time_elapsed too, to make sure that if the loop took too long
    # due to the radio beeing in blocking mode we don't miss packets
    elif time_elapsed_secondary >= 500 or time_elapsed >= 500:
        sendToGround(radio, struct.pack(FMT_STRING_PRIMARY, msg_type, time, *bme_vals))

    if msg_type == PACKET_KIND_SECONDARY:
        last_secondary = ticks_ms()

    last_time = ticks_ms()
    

    
