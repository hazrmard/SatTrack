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
import struct
from .helpers import *


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
        self.tle = None

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
        self.observer.epoch = ephem.Date(str(datetime.utcnow()))
        self.observer.date = ephem.Date(str(datetime.utcnow()))

    def _update_coords(self, t, trace):
        """
        This function runs in a thread started in 'begin_computing' and recomputes the satellites position after
        interval 't'.
        :param t: Interval between computations
        """
        while True:
            with self.lock:
                try:
                    if trace > 0:
                        self.observer.date = ephem.Date(self.observer.date + trace * ephem.second)
                    else:
                        self.observer.date = ephem.Date(str(datetime.utcnow()))
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
                az = to_degs(self.satellite.az)
                alt = to_degs(self.satellite.alt)
            if self._isActive:
                if abs(az - self.azmotor.current_pos) >= self.azmotor.resolution:
                    self.azmotor.move(int(az))
                if abs(alt - self.altmotor.current_pos) >= self.altmotor.resolution:
                    self.altmotor.move(int(alt))
            time.sleep(t)

    def begin_computing(self, interval=1.0, trace=0.0, display=False):
        """
        Starts a thread that computes satellite's coordinates in real time based on the observer's coordinates.
        :param interval: Time between computations.
        :param display: To show a map with the satellite's location.
        """
        self.interval = interval
        t = th.Thread(target=self._update_coords, args=[interval, trace])
        t.daemon = True
        self.threads['tracker'] = t
        t.start()

    def visualize(self):
        self.server.add_source(self)
        self.server.start_server()
        url = 'http://' + str(self.server.host) + ':' + str(self.server.port) + '/' + self.id + '/'
        url = sanitize_url(url)
        print "opening URL: " + url
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
            vertically = (to_degs(self.satellite.alt) >= self.altmotor.range[0] + self.altmotor.pos0) and (to_degs(self.satellite.alt) <= self.altmotor.range[1] + self.altmotor.pos0)
            horizontally = (to_degs(self.satellite.az) >= self.azmotor.range[0] + self.azmotor.pos0) and (to_degs(self.satellite.az) <= self.azmotor.range[1] + self.azmotor.pos0)
            return vertically and horizontally

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
        self.tle = data
        self.id = sanitize(data[0])
        return data

    def next_pass(self, datestr=None, convert=True):
        """
        Takes date as string (or defaults to current time) to compute the next closest pass of a satellite for the
        observer. Times are returned in local time zone, and angles are returned in degrees.
        :param datestr: string containing date
        :param convert: whether or not to convert to time string/ angle degrees
        :return: a dictionary of values
        """
        if datestr is not None:
            date = parser.parse(datestr)
            date = date.replace(tzinfo=tz.tzlocal())
            dateutc = ephem.Date(str(date.astimezone(tz.tzutc())))
        else:
            dateutc = ephem.Date(str(datetime.utcnow()))
        observer = ephem.Observer()             # create a copy of observer
        observer.lon = self.observer.lon
        observer.lat = self.observer.lat
        observer.elev = self.observer.elev
        observer.epoch = self.observer.epoch
        observer.date = ephem.Date(dateutc + ephem.minute)
        satellite = ephem.readtle(self.tle[0], self.tle[1], self.tle[2])        # make a copy of satellite
        satellite.compute(observer)
        next_pass = observer.next_pass(satellite)
        if convert:
            next_pass = {'risetime': tolocal(next_pass[0]), 'riseaz': to_degs(next_pass[1]), 'maxtime': tolocal(next_pass[2])
                        , 'maxalt': to_degs(next_pass[3]), 'settime': tolocal(next_pass[4]), 'setaz': to_degs(next_pass[5])}
        else:
            next_pass = {'risetime': next_pass[0], 'riseaz': next_pass[1], 'maxtime': next_pass[2]
                        , 'maxalt': next_pass[3], 'settime': next_pass[4], 'setaz': next_pass[5]}
        return next_pass

    def next_passes(self, n, startdate=None, convert=True):
        """
        calculate the next n passes starting from the given date (or default to current time). Dates calculated are
        in local time.
        :param n: number of passes to calculate
        :param startdate: earliest time to calculate from
        :param convert: convert to degree angles and string dates?
        :return: a list of dictionaries for each pass
        """
        result = []
        for i in range(n):
            result.append(self.next_pass(startdate, convert))
            startdate = str(result[i]['settime'])
        return result

    def get_tle(self, noradid, destination=None):
        """
        parses n2yo.com for satellite's TLE data using its NORAD id.
        :param noradid: Satellite's NORAD designation
        :param destination: Place to save the data for later use (optional).
        """
        data = parse_text_tle(noradid, AMSAT_URL)
        if not data:
            data = parse_text_tle(noradid, base_CELESTRAK_URL, CELESTRAK_paths)
        if destination is not None:             # write to destination if provided
            f = open(destination, 'wb')
            data = [str(noradid)] + data
            f.writelines(data)
            f.close()
        self.satellite = ephem.readtle(noradid, data[0], data[1])
        self.tle = [str(noradid), data[0], data[1]]
        self.id = sanitize(str(noradid))
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
        self.port.write(struct.pack('>h',angle)[0])
        self.port.write(struct.pack('>h',angle)[1])
        self.current_pos = angle


def store_passes(satellite, outpath, n=100):
    data = satellite.next_passes(n)
    import csv
    keys = ['risetime', 'riseaz', 'maxtime', 'maxalt', 'settime', 'setaz']
    with open(outpath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


if __name__ == '__main__':
   pass

