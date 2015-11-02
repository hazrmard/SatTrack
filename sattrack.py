__author__ = 'Ibrahim'

import ephem
from datetime import datetime
import requests
from lxml import html
import time
import threading as th


class SatTrack:
    def __init__(self):
        self.observer = ephem.Observer()
        self.satellite = None
        self.threads = []
        self.lock = th.Lock()
        self.interval = 1

    def set_location(self, lat='36.1486', lon='-86.8050', ele=182):
        self.observer.lat = lat
        self.observer.lon = lon
        self.observer.elev = ele
        self.observer.epoch = datetime.utcnow()
        self.observer.date = datetime.utcnow()

    def _update(self, t):
        while True:
            with self.lock:
                self.observer.date = datetime.utcnow()
                self.satellite.compute(self.observer)
            time.sleep(t)

    def begin(self, interval=1):
        self.interval = interval
        t = th.Thread(target=self._update, args=[interval])
        t.daemon = True
        self.threads.append(t)
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
        try:
            if destination is not None:             # write to destination if provided
                f = open(destination, 'wb')
                data = [str(noradid)] + data
                f.writelines(data)
                f.close()
            self.satellite = ephem.readtle(str(noradid), data[0], data[1])
        finally:
            return data


    def show_position(self):
        i = 0
        while True:
            i += 1
            with self.lock:
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


if __name__ == '__main__':
    s = SatTrack()
    s.set_location()
    s.load_tle('fox1.tle')
    #s.get_tle(40967)
    print s.observer.next_pass(s.satellite)
    s.begin()
    s.show_position()
    s.threads[1].join()
    s.threads[0].join()
