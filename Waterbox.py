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
        server stopped\n
"""

import json
import signal
import sys
import time

#import Adafruit_DHT
#import RPi.GPIO as GPIO
import requests
#from gps import *

#GPIO.setmode(GPIO.BCM)


# deviceID
devID = 4711

# GPIO Ports on the PI
SONIC_TIME_TRIGGER = 18
SONIC_TIME_ECHO = 24
TEMPERATURE_SENSOR = 23

# Setup sonic sensor
#GPIO.setup(SONIC_TIME_TRIGGER, GPIO.OUT)
#GPIO.setup(SONIC_TIME_ECHO, GPIO.IN)

# Setup humidity-, temperature-sensor
#humiditytempsensor = Adafruit_DHT.DHT22

# Setup GPS Sensor
#gpsSession = gps("localhost", "2947")
#gpsSession.stream(WATCH_ENABLE | WATCH_NEWSTYLE)

# Setup REST-Data
ipaddress = "http://hmpblv.markab.uberspace.de:63837/data/{devid}".format(devid=devID)


def get_distance():
    """HCSR04 sends a sonic signal and is notified when the signal returns
        this function returns the time that elapsed between the sensors

    :return: time between sending and receiving the sonic signal
    """

   # GPIO.output(SONIC_TIME_TRIGGER, True)

    time.sleep(0.00001)
    #GPIO.output(SONIC_TIME_TRIGGER, False)

    starttime = time.time()
    stoptime = time.time()

    counter = 0

  #  while GPIO.input(SONIC_TIME_ECHO) == 0:
   #     starttime = time.time()
    #    counter += 1
     #   if counter > 100000:
      #      return -1

    counter = 0

    #while GPIO.input(SONIC_TIME_ECHO) == 1:
     #   stoptime = time.time()
      #  counter += 1
       # if counter > 100000:
        #    return -1

    sonictime = stoptime - starttime
    return (sonictime * 34300)/2


def get_temperature_humidity():
    """Gets data from the AM2302 humidity and temperature sensor
       and returns the data in a tupel which contains humidity and temperature

    :return: tupel with humidity and temperature
    """

    return 0#Adafruit_DHT.read_retry(humiditytempsensor, TEMPERATURE_SENSOR)


def get_gps_data():
    """"Gets data from the adafruit Ultimate GPS sensor und returns a list with latitude and longitude

    :return: list with latitude and longitude
    """
    gpsc = 0#GpsController()

    gpsc.start()

    gpsdata = [0, 0]
    gpsdata[0] = gpsc.fix.latitude
    gpsdata[1] = gpsc.fix.longitude

    gpsc.stopController()

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
    print("""CTRL-C pressed
        \n\r program stoped""")
    #GPIO.cleanup()
    sys.exit(0)


if __name__ == "__main__":
    print("*****Starting Waterbox*****")
    while True:
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
