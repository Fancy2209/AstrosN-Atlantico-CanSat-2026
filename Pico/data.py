from machine import SPI, I2C, UART, Pin, SDCard
from bno_i2c import BNO08X_I2C
from bme280_float import BME280
from adafruit_gps import GPS
import os
import sdcard
import _thread

buffer = []

def io_thread():
    with open("./data.csv", "w") as csv:
        while True:
            if len(buffer) > 0:
                csv.write(buffer.pop(0))
            

    

def setup():
    #Expose sensor to global scope
    global bno
    global bme
    global gps

    #Init Sensors
    bno = BNO08X_I2C(
        I2C(0, sda=Pin(4), scl=Pin(5), freq=400000), 
        0x4A, 
        Pin(14, Pin.OUT), 
        Pin(15, Pin.IN, Pin.PULL_UP)
    )
    bme = BME280(i2c=I2C(0, sda=Pin(4), scl=Pin(5)))
    gps = GPS(UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1)))

    # Mount SDCard
    os.mount(sdcard.SDCard(
        SPI(0, baudrate=1000000, polarity=0, phase=0, 
                    sck=Pin(18), mosi=Pin(19), miso=Pin(16)), #spi 
        Pin(17, Pin.OUT) #cs
    ), "/sd")

    #Enable BNO Features
    bno.acceleration.enable()
    bno.linear_acceleration.enable()
    bno.gravity.enable()
    bno.quaternion.enable()
    bno.gyro.enable()
    bno.magnetic.enable()
    bno.stability_classifier.enable()

def loop():
    bno.update_sensors()
    gps.update()


setup()
_thread.start_new_thread(io_thread , ())
while True:
    loop()
    