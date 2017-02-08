#!/usr/bin/env python2.7
"""This module reads the data of all sensors in an interval of 30 seconds and sends it with a post request
to the MOPEl server.
This script boots automatically after booting the MOPEL Box.

    Interpreter Version:
        **Python2.7**

    Examples:
        $python2.7 Waterbox.py


        *****Starting WaterBox*****\n
        Distance: 46 cm\n
        Humidity: 45% Temperature: 23 degree\n
        Latitude: 45322 Longitude: 56444\n
        Response from Server <201>\n
        CTRL-C pressed\n
        *****Waterbox stopped*****\n
"""

import json
import signal
import sys
import time

import Adafruit_DHT
import RPi.GPIO as GPIO
import requests
from GpsController import GpsController

GPIO.setmode(GPIO.BCM)


# deviceID
devID = 4711

# GPIO Ports on the PI
SONIC_TIME_TRIGGER = 18
SONIC_TIME_ECHO = 24
TEMPERATURE_SENSOR = 23

# Setup sonic sensor
GPIO.setup(SONIC_TIME_TRIGGER, GPIO.OUT)
GPIO.setup(SONIC_TIME_ECHO, GPIO.IN)

# Setup humidity-, temperature-sensor
humiditytempsensor = Adafruit_DHT.DHT22

# Setup GPS Sensor
gpsc = GpsController()

# Setup REST-Data
ipaddress = "http://hmpblv.markab.uberspace.de:63837/data/{devid}".format(devid=devID)


def get_distance():
    """Reads data from the HCSR04-Sonicsensor and returnes the distance

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

    sonictime = stoptime - starttime
    return (sonictime * 34300)/2


def get_temperature_humidity():
    """Gets data from the AM2302-Sensor and returns humidity and temperature

    :return: tupel with humidity and temperature
    """

    return Adafruit_DHT.read_retry(humiditytempsensor, TEMPERATURE_SENSOR)


def get_gps_data():
    """"Gets data from the adafruit Ultimate GPS sensor und returns a list with latitude and longitude

    :return: list with latitude and longitude
    """
    gpsdata = [0, 0]
    gpsdata[0] = gpsc.fix.latitude
    gpsdata[1] = gpsc.fix.longitude
    if gpsdata[0] == "nan" or gpsdata[1] == "nan":
        return [0,0]
    return gpsdata


def send_sensor_data(sensordata):
    """Generates an rest header and sends the data to the server

    :param sensordata: json structure which contains all the sensordata
    :return: send data if no data is send return -1
    """
    data_json = json.dumps(sensordata)
    headers = {'Content-type': 'application/json'}
    return requests.post(ipaddress, data=data_json, headers=headers)


def signal_handler(arg1, argv):
    """Closes the ports and the socketconnection after pushing ctrl-c

    :param arg1: not used
    :param arg2: not used
    :return: none
    """
    print("""CTRL-C pressed\n\r
        ***Waterbox stoped***""")
    gpsc.stopController()
    GPIO.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    print("*****Starting Waterbox*****")
    while True:
        gpsc.start()
        signal.signal(signal.SIGINT, signal_handler)
        distance = get_distance()
        print("Distance {dist} cm\n\r".format(dist=distance))
        humidity, temperature = get_temperature_humidity()
        print("Humidity: {humid} % Temperature: {temp} degree\n\r".format(humid=humidity, temp=temperature))
        latitude, longitude = get_gps_data()
        print("Latitude: {lat} Longitude: {long}\n\r".format(lat=latitude, long=longitude))
        measurementValues = {'lat': latitude, 'lon': longitude, 'degree': temperature,
                             'distance': distance, 'airpressure': 0, 'wet': humidity}
        print("Send data to server")
        response = send_sensor_data(measurementValues)
        print("Response from Server {resp}".format(resp=response))
        time.sleep(30)
