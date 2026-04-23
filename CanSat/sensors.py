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
        i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=100000)
        #print(i2c.scan())
        self.bme = BME280(i2c=i2c)
        
        self.bno = BNO08X_I2C(
            i2c,
            0x4A, 
            Pin(14, Pin.OUT), #reset
            Pin(6, Pin.IN, Pin.PULL_UP) #interrupt
        )
        self.bno.linear_acceleration.enable()
        self.bno.quaternion.enable()
        self.bno.stability_classifier.enable()

        
    def read_bme(self):
        bme = list(self.bme.read_compensated_data())
        return [
            bme[0], #T
            bme[1], #P
            bme[2]  #H
        ]
    
    def read_bno(self):
        return [
            stabilityStrToInt(self.bno.stability_classifier.value), 
            self.bno.linear_acceleration.full[0], # Linear Acceleration X
            self.bno.linear_acceleration.full[1], # Linear Acceleration Y
            self.bno.linear_acceleration.full[2], # Linear Acceleration Z
            self.bno.quaternion.full[0], # Quaternion R
            self.bno.quaternion.full[1], # Quaternion Y
            self.bno.quaternion.full[2], # Quaternion J
            self.bno.quaternion.full[3]  # Quaternion K
        ]
    
    def update(self):
        self.bno.update_sensors()
