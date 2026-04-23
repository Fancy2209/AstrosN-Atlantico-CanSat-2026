
from radio import SX1262Adapter
from sdio import init_sd, send_to_ground
from sensors import Sensors, STABILITY_IN_MOTION, STABILITY_UNKNOWN
from time import ticks_ms, ticks_diff, sleep_ms
from utils_no_atlantico import digitalWrite, LOW, HIGH
import struct, sys#, os

PACKET_KIND_PRIMARY   = 0
PACKET_KIND_SECONDARY = 1

PIN_BUZZER = 21
PIN_LED_BLUE = 26

# TODO: Should I add an header?
FMT_STRING_PRIMARY = "<" + "B" + "I" + "fff"
FMT_STRING_SECONDARY = FMT_STRING_PRIMARY + "B" + "fff" + "ffff"

def beepBeep(num, time):
    for i in range(0, num):
        digitalWrite(PIN_BUZZER, LOW)
        digitalWrite(PIN_BUZZER, HIGH)
        sleep_ms(time)
        digitalWrite(PIN_BUZZER, LOW)
        sleep_ms(time)

no_sd = False
try:
    init_sd()
    print("Yes SDCard")
except Exception as e:
    sys.print_exception(e)
    no_sd = True
    beepBeep(3, 200)

radio = SX1262Adapter()
sensors = Sensors()
last_stability: int = STABILITY_UNKNOWN

last_read = ticks_ms()
last_read_secondary = ticks_ms()
beep = False

beepBeep(1, 200)
digitalWrite(PIN_LED_BLUE, HIGH)

while True:
    try:
        SHOULD_CALM_DOWN = last_stability not in (STABILITY_UNKNOWN, STABILITY_IN_MOTION)

        if (not SHOULD_CALM_DOWN) and beep:
            beep = False
            digitalWrite(PIN_BUZZER, LOW)

        sensors.update()

        msg_type = PACKET_KIND_PRIMARY
        bme_vals = sensors.read_bme()

        time_elapsed = ticks_diff(ticks_ms(), last_read)
        ticks_mstime_elapsed_secondary = ticks_diff(ticks_ms(), last_read_secondary)

        if (ticks_mstime_elapsed_secondary >= 1_000 and not SHOULD_CALM_DOWN) or (ticks_mstime_elapsed_secondary >= 10_000 and SHOULD_CALM_DOWN):
            msg_type = PACKET_KIND_SECONDARY
            bno_vals = sensors.read_bno()
            sleep_ms(50)
            if not SHOULD_CALM_DOWN:
                pack = struct.pack(FMT_STRING_SECONDARY, msg_type, ticks_ms(), 
                    bme_vals[0], bme_vals[1], bme_vals[2],             # BME
                    bno_vals[0],                                       # Stability
                    bno_vals[1], bno_vals[2], bno_vals[3],             # Linear Acceleration
                    bno_vals[4], bno_vals[5], bno_vals[6], bno_vals[7] # Quaternion
                )
                send_to_ground(radio, pack, no_sd, msg_type)
                print(struct.unpack(FMT_STRING_SECONDARY, pack))
            last_stability = bno_vals[0]
            last_read_secondary = ticks_ms()

        if SHOULD_CALM_DOWN:
            beep = not beep
            digitalWrite(PIN_BUZZER, beep)
        else:
            beep = False
            digitalWrite(PIN_BUZZER, False)

        # we check for time_elapsed too, to make sure that if the loop took too long
        # due to the radio beeing in blocking mode we don't miss packets
        if (SHOULD_CALM_DOWN and (time_elapsed >= 10_000)) or (not SHOULD_CALM_DOWN and (time_elapsed >= 500)):
            pack = struct.pack(FMT_STRING_PRIMARY, msg_type, ticks_ms()/1000, bme_vals[0], bme_vals[1], bme_vals[2])
            send_to_ground(radio, pack, no_sd, msg_type)
            print(struct.unpack(FMT_STRING_PRIMARY, pack))
            last_read = ticks_ms()
    except Exception as exp:
        print("Died")
        sys.print_exception(exp)
        # Doesn't trigger
        #if isinstance(exp, KeyboardInterrupt):
        #    digitalWrite(PIN_BUZZER, LOW)
        #    digitalWrite(PIN_LED_BLUE, LOW)
        #    digitalWrite(PIN_BUZZER, LOW)
        #    print(sdFile.readline())
        #    sdFile.close()
        #    os.umount("/sd")
        #    break
        


    

    
