__author__ = 'Ibrahim'

import ephem
from datetime import datetime
import requests
from lxml import html
import time
import threading as th
import serial
from interface import *
import webbrowser as wb
# import matplotlib.pyplot as plt
# from mpl_toolkits.basemap import Basemap
# import numpy as np


class SatTrack:
    def __init__(self):
        self.id = None
        self.observer = ephem.Observer()
        self.satellite = None
        self.threads = {}
        self.lock = th.Lock()
        self.interval = 1
        self._isActive = False
        self.azmotor = None
        self.altmotor = None
        self.server = Server()

    def set_location(self, lat='36.1486', lon='-86.8050', ele=182):
        """
        Sets location of observer using coordinates (+N and +E). Defaults to Vanderbilt University's coordinates.
        :param lat: Observer's latitude (positive north from the equator)
        :param lon: Observer's longitide (positive east from the prime meridian)
        :param ele: Observer's elevation above sea level.
        """
        self.observer.lat = lat
        self.observer.lon = lon
        self.observer.elev = ele
        self.observer.epoch = datetime.utcnow()
        self.observer.date = datetime.utcnow()

    def _update_coords(self, t):
        """
        This function runs in a thread started in 'begin_computing' and recomputes the satellites position after
        interval 't'.
        :param t: Interval between computations
        """
        while True:
            with self.lock:
                try:
                    self.observer.date = datetime.utcnow()
                    self.satellite.compute(self.observer)
                    self._isActive = True
                except:
                    self._isActive = False
            time.sleep(t)

    def _update_tracker(self, t):
        """
        This function runs in a thread started by 'begin_tracking' and moves altitude and azimuth servo motors every
        't' seconds if the change in coordinates is greater than the motors' resolutions.
        :param t: Interval between commands to motors.
        """
        while True:
            with self.lock:
                az = todegs(self.satellite.az)
                alt = todegs(self.satellite.alt)
            if self._isActive:
                if abs(az - self.azmotor.current_pos) >= self.azmotor.resolution:
                    self.azmotor.move(int(az))
                if abs(alt - self.altmotor.current_pos) >= self.altmotor.resolution:
                    self.altmotor.move(int(alt))
            time.sleep(t)

    def begin_computing(self, interval=1, display=False):
        """
        Starts a thread that computes satellite's coordinates in real time based on the observer's coordinates.
        :param interval: Time between computations.
        :param display: To show a map with the satellite's location.
        """
        self.interval = interval
        t = th.Thread(target=self._update_coords, args=[interval])
        t.daemon = True
        self.threads['tracker'] = t
        t.start()

    def visualize(self):
        self.server.add_source(self)
        self.server.start_server()
        url = 'http://' + str(self.server.host) + ':' + str(self.server.port) + '/' + self.id
        wb.open(url, new=2)


    def connect_servos(self, port=2, minrange=(0, 0), maxrange=(180, 360), initpos=(0, 0)):
        """
        Connects computer to arduino which has a pair of servos connected. Initializes motors to their default positions
        :param port: port name/number e.g 'COM3' on a PC, '/dev/ttyUSB0' on Linux, '/dev/tty.usbserial-FTALLOK2' on Mac
        :param minrange: A touple containing the minimum angle for (altitude, azimuth) motors
        :param maxrange: A touple containing the maximum angle for (altitude, azimuth) motors
        :param initpos: A touple containing the initial orientation angle for (altitude, azimuth) motors
        """
        servos = ServoController(2, port)
        self.azmotor, self.altmotor = servos.motors
        self.altmotor.range[0] = minrange[0]
        self.azmotor.range[0] = minrange[1]
        self.altmotor.range[1] = maxrange[0]
        self.azmotor.range[1] = maxrange[1]
        self.altmotor.pos0 = initpos[0]
        self.azmotor.pos0 = initpos[1]
        self.azmotor.initialize()
        self.altmotor.initialize()

    def begin_tracking(self, interval=None):
        """
        Begins a thread that sends periodic commands to servo motors.
        :param interval: Time between commands in seconds.
        :return:
        """
        if interval is None:
            interval = self.interval
        t = th.Thread(target=self._update_tracker, args=[interval])
        t.daemon = True
        self.threads['motors'] = t
        t.start()

    def is_trackable(self):
        """
        Checks if the satellite's current position can be tracked by the motors (accounting for range and orientation)
        """
        with self.lock:
            vertically = (todegs(self.satellite.alt) >= self.altmotor.range[0] + self.altmotor.pos0) and (todegs(self.satellite.alt) <= self.altmotor.range[1] + self.altmotor.pos0)
            hozizontally = (todegs(self.satellite.az) >= self.azmotor.range[0] + self.azmotor.pos0) and (todegs(self.satellite.az) <= self.azmotor.range[1] + self.azmotor.pos0)
            return vertically and hozizontally

    def is_observable(self):
        """
        Checks if the satellite can be seen above the horizon
        """
        with self.lock:
            return self.satellite.alt >= self.observer.horizon

    def load_tle(self, filename):
        """
        loads satellite TLE data from a text file
        :param filename: path of file
        """
        f = open(filename, 'rb')
        data = f.readlines()
        f.close()
        self.satellite = ephem.readtle(data[0], data[1], data[2])
        self.id = sanitize(data[0])
        return data

    def get_tle(self, noradid, destination=None):
        """
        parses n2yo.com for satellite's TLE data using its NORAD id.
        :param noradid: Satellite's NORAD designation
        :param destination: Place to save the data for later use (optional).
        """
        url = 'http://www.n2yo.com/satellite/?s=' + str(noradid)
        page = requests.get(url)                # getting html data
        tree = html.fromstring(page.text)       # converting to tree format for parsing
        data = tree.xpath('//div/pre/text()')   # remove all newline and whitespace
        data = data[0].rstrip().strip('\r').strip('\n')     # remove \r and \n
        data = data.splitlines()
        if destination is not None:             # write to destination if provided
            f = open(destination, 'wb')
            data = [str(noradid)] + data
            f.writelines(data)
            f.close()
        self.satellite = ephem.readtle(sanitize(noradid), data[0], data[1])
        self.id = str(noradid)
        return data

    def show_position(self):
        """
        prints satellite's coordinates and relative position periodically.
        """
        i = 0
        while True:
            i += 1
            with self.lock:
                if self._isActive:
                    print('#' + str(i) + ', Azimuth: ' + str(self.satellite.az) + ', Altitude: ' + str(self.satellite.alt) +
                          ' Lat: ' + str(self.satellite.sublat) + ' Long: ' + str(self.satellite.sublong) + '\r'),
            time.sleep(self.interval)

    def write_to_file(self, fname, secs):
        i = 0
        f = open(fname, 'wb')
        while i < secs:
            i += 1
            with self.lock:
                f.write('#' + str(i) + ' Azimuth: ' + str(self.satellite.az) + ' Altitude: ' + str(self.satellite.alt) + '\n')
            time.sleep(self.interval)
        f.close()


class ServoController:
    def __init__(self, motors=2, port=2, baudrade=9600, timeout=1):
        self.port = port
        self.baudrate = baudrade
        self.timeout = timeout
        try:
            self.serial = serial.Serial(port, baudrade, timeout=timeout)
        except serial.SerialException as e:
            print e.message
        self.motors = [Motor(i, self.serial) for i in range(motors)]


class Motor:
    def __init__(self, id, port):
        self.motor = id
        self.resolution = 1
        self.range = (0, 180)
        self.current_pos = 0
        self.pos0 = 0
        self.port = port

    def initialize(self):
        self.move(self.range[0])

    def move(self, angle):
        angle -= self.pos0
        if angle < self.range[0] or angle > self.range[1]:
            raise ValueError('Angle out of range.')
        self.port.write(chr(255))
        self.port.write(chr(self.motor))
        self.port.write(chr(angle))
        self.current_pos = angle


def todegs(rads):
    return rads * 180 / ephem.pi


def sanitize(string):
    return str(''.join([x for x in string if x.isalnum()]))


def main():
    s = SatTrack()
    print 'Initialized...'
    s.set_location()
    print 'Location set...'
    s.load_tle('fox1.tle')
    print 'Satellite data loaded. ID:', s.id
    #s.get_tle(40967)
    print '\nComputing next pass (UTC):'
    print s.observer.next_pass(s.satellite)
    s.begin_computing()
    print 'Starting real-time coordinate tracking...'
    #s.connect_servos(minrange=(10, 10), maxrange=(170, 170))
    #s.begin_tracking()
    s.visualize()
    #s.show_position()
    print 'Front end server set up...'
    i = input('Exit? ... ')
    if i =='y':
        s.server.stop_server()
    print 'server closed'

if __name__ == '__main__':
   main()

