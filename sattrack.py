__author__ = 'Ibrahim'

import ephem
from datetime import datetime
import requests
from lxml import html
import time
import threading as th
import serial


class SatTrack:
    def __init__(self):
        self.observer = ephem.Observer()
        self.satellite = None
        self.threads = {}
        self.lock = th.Lock()
        self.interval = 1
        self._isActive = False
        self.azmotor = None
        self.altmotor = None

    def set_location(self, lat='36.1486', lon='-86.8050', ele=182):
        self.observer.lat = lat
        self.observer.lon = lon
        self.observer.elev = ele
        self.observer.epoch = datetime.utcnow()
        self.observer.date = datetime.utcnow()

    def _update_coords(self, t):
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
        while True:
            with self.lock:
                if self._isActive:
                    if abs(self.satellite.az*180/ephem.pi - self.azmotor.current_pos) >= self.azmotor.resolution:
                        self.azmotor.move(int(self.satellite.az*180/3.141))
                    if abs(self.satellite.alt*180/ephem.pi - self.altmotor.current_pos) >= self.altmotor.resolution:
                        self.altmotor.move(int(abs(self.satellite.alt*180/ephem.pi)))
            time.sleep(t)

    def begin_computing(self, interval=1):
        self.interval = interval
        t = th.Thread(target=self._update_coords, args=[interval])
        t.daemon = True
        self.threads['tracker'] = t
        t.start()

    def begin_tracking(self, interval=1):
        servos = ServoController(2)
        self.azmotor, self.altmotor = servos.initialize()
        t = th.Thread(target=self._update_tracker, args=[interval])
        t.daemon = True
        self.threads['motors'] = t
        t.start()

    def load_tle(self, filename):
        f = open(filename, 'rb')
        data = f.readlines()
        f.close()
        self.satellite = ephem.readtle(data[0], data[1], data[2])
        return data

    def get_tle(self, noradid, destination=None):
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
        self.satellite = ephem.readtle(str(noradid), data[0], data[1])
        return data

    def show_position(self):
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

    def initialize(self):
        for motor in self.motors:
            motor.initialize()
        return self.motors


class Motor:
    def __init__(self, id, port):
        self.motor = id
        self.resolution = 1
        self.range = (0, 180)
        self.current_pos = 0
        self.port = port

    def initialize(self):
        self.move(self.range[0])

    def move(self, angle):
        if angle < self.range[0] or angle > self.range[1]:
            raise ValueError('Angle out of range.')
        self.port.write(chr(255))
        self.port.write(chr(self.motor))
        self.port.write(chr(angle))
        self.current_pos = angle

if __name__ == '__main__':
    s = SatTrack()
    s.set_location()
    s.load_tle('fox1.tle')
    #s.get_tle(40967)
    print s.observer.next_pass(s.satellite)
    s.begin_computing()
    s.begin_tracking()
    s.show_position()
