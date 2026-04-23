
from radio import SX1262Adapter
from sdio import init_sd, send_to_ground
from sensors import Sensors, STABILITY_UNKNOWN, STABILITY_STATIONARY, STABILITY_ON_TABLE, STABILITY_STABLE
from time import ticks_ms, ticks_diff, sleep_ms
from utils_no_atlantico import digitalWrite
import struct, os, machine, sys

PACKET_KIND_PRIMARY   = 0
PACKET_KIND_SECONDARY = 1

# TODO: Should I add an header?
FMT_STRING_PRIMARY = "<" + "B" + "I" + "fff"
FMT_STRING_SECONDARY = FMT_STRING_PRIMARY + "B" + "fff"# + "ff"

no_sd = False
try:
    init_sd()
    print("Yes SDCard")
except Exception as e:
    print(e)
    no_sd = True
radio = SX1262Adapter()
sensors = Sensors()
last_stability: int = STABILITY_UNKNOWN

last_read = ticks_ms()
last_read_secondary = ticks_ms()
beep = False
while True:
    try:
        SHOULD_CALM_DOWN = (last_stability == STABILITY_STATIONARY or last_stability == STABILITY_ON_TABLE or last_stability == STABILITY_STABLE)

        if (not SHOULD_CALM_DOWN) and beep:
            beep = False
            digitalWrite(21, False)

        sensors.update()

        msg_type = PACKET_KIND_PRIMARY
        bme_vals = sensors.read_bme()

        time_elapsed = ticks_diff(ticks_ms(), last_read)
        ticks_mstime_elapsed_secondary = ticks_diff(ticks_ms(), last_read_secondary)

        if (ticks_mstime_elapsed_secondary >= 1000 and not SHOULD_CALM_DOWN) or (ticks_mstime_elapsed_secondary >= 10000 and SHOULD_CALM_DOWN):
            msg_type = PACKET_KIND_SECONDARY
            bno_vals = sensors.read_bno()
            sleep_ms(50)
            if not SHOULD_CALM_DOWN:
                gps_vals = sensors.read_gps()
                pack = struct.pack(FMT_STRING_SECONDARY, msg_type, ticks_ms(), 
                    bme_vals[0], bme_vals[1], bme_vals[2],
                    bno_vals[0], 
                    bno_vals[1], bno_vals[2], bno_vals[3]
                )
                send_to_ground(radio, pack, no_sd)
                print(struct.unpack(FMT_STRING_SECONDARY, pack))
            last_stability = bno_vals[0]
            last_read_secondary = ticks_ms()

        # we check for time_elapsed too, to make sure that if the loop took too long
        # due to the radio beeing in blocking mode we don't miss packets
        if (SHOULD_CALM_DOWN and (time_elapsed >= 10_000)) or (not SHOULD_CALM_DOWN and (time_elapsed >= 500)):
            if SHOULD_CALM_DOWN and (time_elapsed >= 10_000):
                digitalWrite(21, beep)
                print(beep)
                beep = not beep
            pack = struct.pack(FMT_STRING_PRIMARY, msg_type, ticks_ms(), bme_vals[0], bme_vals[1], bme_vals[2])
            send_to_ground(radio, pack, no_sd)
            print(struct.unpack(FMT_STRING_PRIMARY, pack))
            last_read = ticks_ms()
    except Exception as exp:
        print("Died")
        sys.print_exception(e)
        if isinstance(exp, KeyboardInterrupt):
            os.umount("/sd")
            break


    

    
