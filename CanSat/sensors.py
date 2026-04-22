from bno_i2c import BNO08X_I2C
from bme280_float import BME280
from adafruit_gps import GPS
from machine import UART, I2C, Pin

STABILITY_UNKNOWN = 0
STABILITY_ON_TABLE = 1
STABILITY_STATIONARY = 2
STABILITY_STABLE = 3
STABILITY_IN_MOTION = 4

# TODO: FIX YOUR PINS!!!!!!

def stabilityStrToInt(str) -> int:
    if   (str == "Unknown"):    return 0
    elif (str == "On Table"):   return 1
    elif (str == "Stationary"): return 2
    elif (str == "Stable"):     return 3
    elif (str == "In motion"):  return 4
    else: return 0

class Sensors():
    def __init__(self):
        i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000)

        self.bme = BME280(i2c=i2c)
        
        self.gps = GPS(UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1)))
        self.gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.gps.send_command(b"PMTK220,1000")
        

        self.bno = BNO08X_I2C(
            i2c,
            0x4A, 
            Pin(4, Pin.OUT), #reset
            Pin(3, Pin.IN, Pin.PULL_UP) #interrupt
        )
        self.bno.linear_acceleration.enable()
        self.bno.quaternion.enable()
        self.bno.stability_classifier.enable()

    def read_bme(self):
        return list(self.bme.read_compensated_data())
    
    def read_bno(self):
        return [
            stabilityStrToInt(self.bno.stability_classifier.value), 
            *list(self.bno.linear_acceleration), 
            *list(self.bno.quaternion)
        ]
    
    def read_gps(self):
        return [
            self.gps.latitude,
            self.gps.longitude
        ]

    def update(self):
        self.bno.update_sensors()
        self.gps.update()
