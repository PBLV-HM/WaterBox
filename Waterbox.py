import json
import time

import  RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

SONIC_TIME_TRIGGER = 18
SONIC_TIME_ECHO = 24

GPIO.setup(SONIC_TIME_TRIGGER, GPIO.OUT)
GPIO.setup(SONIC_TIME_ECHO, GPIO.IN)

def get_sonic_time():
    """HCSR04 sends a sonic signal and is notified when the signal returns
        this function returns the time that elapsed between the sensors

    :return: time between sending and receiving the sonic signal
    """

    GPIO.output(SONIC_TIME_TRIGGER,True)

    time.sleep(0.00001)
    GPIO.output(SONIC_TIME_TRIGGER,False)

    starttime = time.time()
    stoptime = time.time()

    while GPIO.input(SONIC_TIME_ECHO) == 0:
        starttime = time.time()

    while GPIO.input(SONIC_TIME_ECHO) == 1:
        stoptime = time.time()

    return stoptime - starttime

def get_temperature():
    """Gets data from the AM2302 humidity and temperature sensor
       and returns the data in a tupel which contains humidity and temperature

    :return: tupel with humidity and temperature
    """
    sensor = Adafruit_DHT.DHT22
    gpio = 4

    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
    returnlist = humidity,temperature
    return returnlist


def get_air_pressure():

    return 0

def get_gps_data():
    return 0


if __name__ == "__main__":
    while True:
        sonictime = get_sonic_time()
        print("Distance: ",(sonictime*34300)/2)
        temperature = get_temperature()
        airpressure = get_air_pressure()
        gpsdata = get_gps_data()
        measurementValues = json.dumps(
            dict(sonic_time=sonictime, temperature=temperature, airpressure=airpressure, gpsdata=gpsdata))
        time.sleep(1)