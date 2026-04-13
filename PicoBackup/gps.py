from machine import Pin,I2C,UART  #***************
import time

GPS = UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))
# The following line ensures that the GPS reports the GPVTG NMEA Sentence
GPS.write(b"$PMTK314,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0*28\r\n")
try:
    while True:
        if GPS.any():
            #myChar=GPS.read(1)
            myChar=GPS.read(1).decode('utf-8')
            print(myChar, end="") #Supress the line feed, so It continues to print across
except KeyboardInterrupt:
    print("\nStopping program... Cleaning up UART.")
    GPS.deinit()  # Properly release UART before exit
    time.sleep(1)  # Short pause to ensure clean shutdown
    print("Exited cleanly.")
