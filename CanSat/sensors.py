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
        #self.bno.quaternion.enable()
        self.bno.stability_classifier.enable()

        self.gps = GPS(UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1)))
        self.gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
        self.gps.send_command(b"PMTK220,1000")
        
    def read_bme(self):
        bme = list(self.bme.read_compensated_data())
        return [
            bme[0],
            bme[1],
            bme[2]
        ]
    
    def read_bno(self):
        linear_acceleration = list(self.bno.linear_acceleration)
        return [
            stabilityStrToInt(self.bno.stability_classifier.value), 
            linear_acceleration[0], 
            linear_acceleration[1], 
            linear_acceleration[2], 
            #list(self.bno.quaternion)[0],
            #list(self.bno.quaternion)[1],
            #list(self.bno.quaternion)[2],
            #list(self.bno.quaternion)[3]
        ]
    
    def read_gps(self):
        return [
            self.gps.latitude,
            self.gps.longitude
        ]

    def update(self):
        self.bno.update_sensors()
        self.gps.update()
