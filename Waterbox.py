import json
import signal
import socket
import sys
import time

import Adafruit_DHT
import gps

import RPi.GPIO as GPIO

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

# Setup GPS Sensor
gpsSession = gps.gps("localhost", "2947")
gpsSession.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

# Setup REST-Data
ipaddress = "127.0.0.1"
port = "80"
restsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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

    humidity, temp = Adafruit_DHT.read_retry(humiditytempsensor, TEMPERATURE_SENSOR)
    returnlist = humidity, temp
    return returnlist


def get_air_pressure():
    return 0


def get_gps_data():
    """"Gets data from the adafruit Ultimate GPS sensor und returns a list with latitude and longitude

    :return: list with latitude and longitude
    """
    gpsc = gps.GpsController()

    gpsc.start()

    gpsdata = [0, 0]
    gpsdata[0] = gpsc.fix.latitude
    gpsdata[1] = gpsc.fix.longitude

    gpsc.stopController()

    return gpsdata


def connect_with_rest_interface():
    """Establish the connection with the REST server

    :return: statuscode if no error occures return 0
    """
    return restsocket.connect((ipaddress, port))


def disconnect_with_rest_interface():
    """Closes the connection with the REST server

    :return: statuscode if no error occures return 0
    """
    return restsocket.close()


def send_sensor_data(sensordata):
    """Generates an rest header and sends the data to the server


    :param sensordata: json structure which contains all the sensordata
    :return: send data if no data is send return -1
    """
    string = """PUT /sensor/data HTTP/1.1\n\r
                Content-Type: application/json\n\r
                Accept: application/json\n\r
                Content-Length:{datasize}\n\r
                {data}\n\r
    """.format(datasize=len(sensordata), data=sensordata)
    senddata = restsocket.send(string)
    if senddata <= 0:
        return -1
    return sensordata

def signal_handler():
    """Closes the ports and the socketconnection after pushing ctrl-c

    :return:
    """
    print("CTRL-C pressed")
    disconnect_with_rest_interface()
    GPIO.cleanup()
    sys.exit(0)

if __name__ == "__main__":
    connectret = connect_with_rest_interface()
    if connectret != -1:
        while True:
            signal.signal(signal.SIGINT, signal_handler)
            sonictime = get_sonic_time()
            if sonictime != -1:
                print("Distance: {distance} cm\r\n".format(distance=(sonictime * 34300) / 2))
            temperature = get_temperature_humidity()
            print("Temprature {temp} degree\r\n".format(temp=temperature[1]))
            print ("Humidity {humidity} %\r\n".format(humidity=temperature[0]))
            airpressure = get_air_pressure()
            gpsdata = get_gps_data()
            print(
            "GPSData: latitude: {latitude}, longitude: {longitude}".format(latitude=gpsdata[0], longitude=gpsdata[1]))
            measurementValues = json.dumps(
                dict(sonic_time=sonictime, temperature=temperature, airpressure=airpressure, gpsdata=gpsdata))
            send_sensor_data(measurementValues)
            time.sleep(2)


