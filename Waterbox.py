import time

import Adafruit_DHT

import  RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

# GPIO Ports on the PI
SONIC_TIME_TRIGGER = 18
SONIC_TIME_ECHO = 24
TEMPERATURE_SENSOR = 23

# Setup sonic sensor
GPIO.setup(SONIC_TIME_TRIGGER, GPIO.OUT)
GPIO.setup(SONIC_TIME_ECHO, GPIO.IN)

# Setup humidity-, temperature-sensor
humiditytempsensor = Adafruit_DHT.DHT22


def get_sonic_time():
    """HCSR04 sends a sonic signal and is notified when the signal returns
        this function returns the time that elapsed between the sensors

    :return: time between sending and receiving the sonic signal
    """

    GPIO.output(SONIC_TIME_TRIGGER, True)

    time.sleep(0.00001)
    GPIO.output(SONIC_TIME_TRIGGER, False)

    starttime = time.time()
    stoptime = time.time()

    counter = 0

    while GPIO.input(SONIC_TIME_ECHO) == 0:
        starttime = time.time()
        counter += 1
        if counter > 100000:
            return -1

    counter = 0

    while GPIO.input(SONIC_TIME_ECHO) == 1:
        stoptime = time.time()
        counter += 1
        if counter > 100000:
            return -1

    return stoptime - starttime


def get_temperature_humidity():
    """Gets data from the AM2302 humidity and temperature sensor
       and returns the data in a tupel which contains humidity and temperature

    :return: tupel with humidity and temperature
    """

    humidity, temperature = Adafruit_DHT.read_retry(humiditytempsensor, TEMPERATURE_SENSOR)
    returnlist = humidity, temperature
    return returnlist


def get_air_pressure():

    return 0


def get_gps_data():
    return 0


if __name__ == "__main__":
    while True:
        sonictime = get_sonic_time()
        if sonictime != -1:
            print("Distance: {distance} cm\r\n".format(distance=(sonictime*34300)/2))
        temperature = get_temperature_humidity()
        print("Temprature {temp} degree\r\n".format(temp =temperature[1]))
        print ("Humidity {humidity} %\r\n".format(humidity = temperature[0]))
        airpressure = get_air_pressure()
        #gpsdata = get_gps_data()
        #measurementValues = json.dumps(
         #   dict(sonic_time=sonictime, temperature=temperature, airpressure=airpressure, gpsdata=gpsdata))
        time.sleep(2)