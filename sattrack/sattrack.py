__author__ = 'Ibrahim'

import ephem
from datetime import datetime
import requests
import time
import threading as th
import serial
from interface import *
import webbrowser as wb
import struct
from .helpers import *
import defaults

MOTOR_DEBUG_MODE = False

class SatTrack:
    def __init__(self):
        self.id = None          # name of satellite (case sensitice, alphanumeric only)
        self.observer = ephem.Observer()    #observer class representing current location
        self.satellite = None               #satellite object created by pyephem
        self.threads = {}                   #dictionary of computing and tracking threads
        self.threads['tracker'] = None
        self.threads['motors'] = None
        self.lock = th.Lock()               #used to do non-threadsafe operations
        self._isActive = False              #flag to see if satellite is computing
        self.azmotor = None                 # azimuth motor, sattrack.Motor()
        self.altmotor = None                # altitude motor, sattrack.Motor()
        self.server = Server()              # sattrack.interface.Server()
        self.tle = None                     # list of 2 line elements read
        self.stopTracking = th.Event()
        self.stopComputing = th.Event()
        self.default_config = {'interval':defaults.interval, 'trace': defaults.trace, 'port':defaults.port, 'motors':defaults.motors, 'pwm':defaults.pwm, 'minrange':defaults.minrange, \
                                        'maxrange':defaults.maxrange, 'lat': defaults.lat, 'lon': defaults.lon, 'ele': defaults.ele, 'initpos': defaults.initpos, 'timeout': defaults.timeout, \
                                        'angle_map': defaults.angle_map, 'baudrate': defaults.baudrate, 'host': defaults.host}
        self.log = ['SatTrack initialized.']
        self.radio = None                   # sattrack.rtlsdr.RtlSdr()

        if MOTOR_DEBUG_MODE:
            print "Debug Mode..."

    def set_location(self, lat=None, lon=None, ele=None):
        """
        Sets location of observer using coordinates (+N and +E). Defaults to Vanderbilt University's coordinates.
        :param lat: Observer's latitude (positive north from the equator)
        :param lon: Observer's longitide (positive east from the prime meridian)
        :param ele: Observer's elevation above sea level.
        """
        lat = self.default_config['lat'] if lat is None else lat
        lon = self.default_config['lon'] if lon is None else lon
        ele = self.default_config['ele'] if ele is None else ele

        self.default_config['lat'] = lat
        self.default_config['lon'] = lon
        self.default_config['ele'] = ele

        self.observer.lat = str(lat)
        self.observer.lon = str(lon)
        self.observer.elev = int(ele)
        self.observer.epoch = ephem.Date(str(datetime.utcnow()))
        self.observer.date = ephem.Date(str(datetime.utcnow()))
        self.put_log('Location ' + str(lat) + 'N; ' + str(lon) + 'E; ' + str(ele) + 'm elevation.')

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
        self.put_log('Loaded TLE from: ' + filename)

    def get_tle(self, sat_id, destination=None):
        """
        parses CELESTRAK and AMSAT for satellite's TLE data using its NORAD id.
        :param sat_id: Satellite's designation
        :param destination: Place to save the data for later use (optional).
        """
        data = parse_text_tle(sat_id, AMSAT_URL)
        if not data:
            data = parse_text_tle(sat_id, base_CELESTRAK_URL, CELESTRAK_paths)
        if not data:
            return False
        if destination is not None:             # write to destination if provided
            f = open(destination, 'wb')
            wdata = [str(sat_id) + '\n'] + [data[0] + '\n'] + [data[1] + '\n']
            f.writelines(wdata)
            f.close()
        self.satellite = ephem.readtle(sat_id, data[0], data[1])
        self.tle = [str(sat_id), data[0], data[1]]
        self.id = sanitize(str(sat_id))
        self.put_log('Found ID: ' + str(sat_id))
        return True

    def begin_computing(self, interval=None, trace=None):
        """
        Starts a thread that computes satellite's coordinates in real time based on the observer's coordinates.
        :param interval: Time between computations.
        :param trace: times satellite computation is sped up
        """
        interval = self.default_config['interval'] if interval is None else interval
        self.default_config['interval'] = interval
        trace = self.default_config['trace'] if trace is None else trace
        self.default_config['trace'] = trace

        if self.threads['tracker']:
            self.put_log("Already computing.")
            print 'Already computing'
            return

        t = th.Thread(target=self._update_coords, args=[interval, trace])
        t.daemon = True
        self.threads['tracker'] = t
        t.start()
        self.server.add_source(self)
        self.put_log('Began computing at interval: ' + str(interval) + 's and trace: ' + str(trace) + 's.')

    def _update_coords(self, t, trace):
        """
        This function runs in a thread started in 'begin_computing' and recomputes the satellites position after
        interval 't'.
        :param t: Interval between computations
        :param trace: times satellite computation is sped up
        """
        while not self.stopComputing.isSet():
            with self.lock:
                try:
                    if trace > 0:
                        self.observer.date = ephem.Date(self.observer.date + trace * ephem.second)
                    else:
                        self.observer.date = ephem.Date(str(datetime.utcnow()))
                    self.satellite.compute(self.observer)
                    self._isActive = True
                except Exception as e:
                    print e
                    self._isActive = False
            time.sleep(t)

    def visualize(self, host=None, port=8000, openbrowser=False):
        """
        Start a local server and visualize satellite position. URL is of the format: http://localhost:8000/<name>/
        <name> is sanitized by removing any non-alphanumeric characters.
        :param openbrowser: False -> start server only, True -> start server and open browser.
        """
        host = self.default_config['host'] if host is None else host

        self.server.host = host
        self.server.port = port
        if not Server.server:
            self.server.start_server(host, new=True)
        if openbrowser:
            url = 'http://localhost' + ':' + str(self.server.port) + '/' + self.id + '/'
            url = sanitize_url(url)
            print "opening URL: " + url
            wb.open(url, new=2)
        self.put_log('Started server at: ' + host)

    def begin_tracking(self, interval=None):
        """
        Begins a thread that sends periodic commands to servo motors.
        :param interval: Time between commands in seconds, defaults to computation interval.
        :return:
        """
        interval = self.default_config['interval'] if interval is None else interval

        if self.threads['motors']:
            self.put_log("Already tracking.")
            print 'Already tracking.'
            return

        t = th.Thread(target=self._update_tracker, args=[interval])
        t.daemon = True
        self.threads['motors'] = t
        t.start()
        self.put_log('Started tracking.')

    def _update_tracker(self, t):
        """
        This function runs in a thread started by 'begin_tracking' and moves altitude and azimuth servo motors every
        't' seconds if the change in coordinates is greater than the motors' resolutions.
        :param t: Interval between commands to motors.
        """
        while not self.stopTracking.isSet():
            with self.lock:
                az = to_degs(self.satellite.az)
                alt = to_degs(self.satellite.alt)
            if self._isActive:
                if abs(az - self.azmotor.current_pos) >= self.azmotor.resolution:
                    self.azmotor.move(int(az))
                if abs(alt - self.altmotor.current_pos) >= self.altmotor.resolution:
                    self.altmotor.move(int(alt))
            time.sleep(t)

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

    def connect_servos(self, port=None, motors=None, minrange=None, maxrange=None, initpos=None, mode='a', pwm=None, angle_map=None, timeout=None):
        """
        Connects computer to arduino which has a pair of servos connected. Initializes motors to their default positions
        :param port: port name/number e.g 'COM3' on a PC, '/dev/ttyUSB0' on Linux, '/dev/tty.usbserial-FTALLOK2' on Mac
        :param minrange: A touple containing the minimum angle for (altitude, azimuth) motors
        :param maxrange: A touple containing the maximum angle for (altitude, azimuth) motors
        :param initpos: A touple containing the initial orientation angle for (altitude, azimuth) motors
        :angle_map: a tuple of functions that map satellite coordinates to numbers sent to the arduino
        :pwm: a tuple of pulse width values used by the servo motors
        :timeout: seconds to wait for the servos to setup
        """
        port = self.default_config['port'] if port is None else port
        motors = self.default_config['motors'] if motors is None else motors
        minrange = self.default_config['minrange'] if minrange is None else minrange
        maxrange = self.default_config['maxrange'] if maxrange is None else maxrange
        initpos = self.default_config['initpos'] if initpos is None else initpos
        pwm = self.default_config['pwm'] if pwm is None else pwm
        angle_map = self.default_config['angle_map'] if angle_map is None else angle_map
        timeout = self.default_config['timeout'] if timeout is None else timeout

        self.default_config['port'] = port
        self.default_config['motors'] = motors
        self.default_config['minrange'] = minrange
        self.default_config['maxrange'] = maxrange
        self.default_config['initpos'] = initpos
        self.default_config['pwm'] = pwm
        self.default_config['angle_map'] = angle_map
        self.default_config['timeout'] = timeout

        if port is None:
            print 'Arduino port not found.'
            return

        servos = ServoController(port=port, motors=motors, mode=mode, pwm=pwm, timeout=timeout)
        time.sleep(timeout * 2)      # interval needed to let arduino finish starting up
        servos.setUp()                  # apply PWM values
        self.altmotor, self.azmotor = servos.motors
        self.altmotor.range = (minrange[0], maxrange[0])
        self.azmotor.range = (minrange[1], maxrange[1])
        self.altmotor.pos0 = initpos[0]
        self.azmotor.pos0 = initpos[1]
        self.altmotor.map = angle_map[0]
        self.azmotor.map = angle_map[1]
        self.azmotor.initialize()      # move to starting positions
        self.altmotor.initialize()
        self.put_log('Connected to serial port: ' + str(port) + ' on motors: ' + str(motors[0]) + ' ,' + str(motors[1]) + '.')

    def start_radio(self, freq, output):
        '''Uses rtlsdr module to connect to a SDR dongle and store output as a wav file.
        :output name of an output file
        :freq center frequency of reception
        '''
        import rtlsdr
        if rtlsdr.STATUS==-1:
            self.put_log('Could not connect to radio. Dependencies not installed.')
            print 'Could not connect to radio. Dependencies not installed.'
            return
        self.radio = rtlsdr.RtlSdr(freq=freq, output=output)
        self.radio.start_radio()

    def stop_radio(self, del_files=True):
        '''Terminate radio process.
        :del_files whether to delete or keep intermediate files
        '''
        self.radio.stop_radio(del_files)

    def decode(self):
        '''decode data file using AMSAT Fox telem package. This calls a python
        wrapper for the java package, which originally was a GUI but has been hacked
        into a makeshift command-line callable application. Still throws GUI error
        dialog boxes. ssh X forwarding should be enabled while using this function.
        '''
        self.radio.decode()

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

    def show_position(self):
        """
        prints satellite's coordinates and relative position periodically.
        """
        i = 0
        while self._isActive:
            i += 1
            with self.lock:
                print('#' + str(i) + ', Azimuth: ' + str(self.satellite.az) + ', Altitude: ' + str(self.satellite.alt) +
                      ' Lat: ' + str(self.satellite.sublat) + ' Lon: ' + str(self.satellite.sublong) + '\r'),
            time.sleep(self.default_config['interval'])

    def curr_pos(self):
        with self.lock:
            return {'alt': to_degs(self.satellite.alt), 'az': to_degs(self.satellite.az), 'lat': to_degs(self.satellite.sublat), 'lon': to_degs(self.satellite.sublong)}


    def write_to_file(self, fname, secs):
        i = 0
        f = open(fname, 'wb')
        while i < secs:
            i += 1
            with self.lock:
                f.write('#' + str(i) + ' Azimuth: ' + str(self.satellite.az) + ' Altitude: ' + str(self.satellite.alt) + '\n')
            time.sleep(self.default_config['interval'])
        f.close()

    def put_log(self, text):
        """Enqueue text to instance log. It can later be dequeued by the interface class to display to the user.
        :text Whatever that it is to be logged. String type.
        """
        self.log.append(str(text))

    def get_log(self):
        log = self.log
        self.log = []
        return log

    def stop_tracking(self):
        self.stopTracking.set()
        try:
            self.threads['motors'].join(timeout=self.default_config['interval'])
            self.threads['motors'] = None
            self.put_log("Stopped tracking.")
        except (AttributeError, LookupError) as e:
            print e
            self.put_log("Not tracking anything.")
        self.stopTracking.clear()

    def stop_computing(self):
        self.stopComputing.set()
        try:
            self.threads['tracker'].join(timeout=self.default_config['interval'])
            self.threads['tracker'] = None
            self.put_log("Stopped computing.")
        except (AttributeError, LookupError) as e:
            self.put_log("Not computing anything.")
        self.stopComputing.clear()

    def stop(self):
        self.stop_computing()
        self.stop_tracking()
        self.server.remove_source(self)
        try:
            ServoController.serial_port.close()
        except:
            pass
        print "stopped"


class ServoController:
    """
    Interface between SatTrack and individual motors.
    """
    serial_port = None

    def __init__(self, port=None, motors=None, mode='a', pwm=None, baudrate=None, timeout=None):
        self.portname = defaults.port if port is None else port
        self.baudrate = defaults.baudrate if baudrate is None else baudrate
        self.timeout = defaults.timeout if timeout is None else timeout
        self.motors = defaults.motors if motors is None else motors
        self.mode = mode
        self.pwm = defaults.pwm if pwm is None else pwm
        try:
            if ServoController.serial_port is not None:
                self.serial = ServoController.serial_port
            else:
                self.serial = serial.Serial(self.portname , self.baudrate, timeout=self.timeout)
                ServoController.serial_port = self.serial
        except serial.SerialException as e:
            print e.message
        self.motors = [Motor(i, self.serial, self.pwm, self.mode) for i in self.motors]

    def setUp(self):
        serial_arg = 'x' + str(self.pwm[0]) + '_' + str(self.pwm[1])
        self.serial.write(serial_arg)
        print self.serial.readline().strip()


class Motor:
    def __init__(self, id, port, pwm=(900, 2100), mode='a'):
        self.motor = id
        self.resolution = 1
        self.range = (0, 360)
        self.current_pos = 0
        self.pos0 = 0
        self.port = port
        self.pwm = pwm
        self.map = lambda x: x
        self.mode = mode

    def initialize(self):
        #midpoint = (self.range[0] + self.range[1]) / 2
        self.move(self.range[0])

    def move(self, angle):
        """
        Checks for out of range angles, maps angle according to to optional Motor.map function, and either writes pulse width
        or angle to serial port.
        """
        if (angle < self.range[0] or angle > self.range[1]) and not MOTOR_DEBUG_MODE:
            raise ValueError('Motor ' + str(self.motor) + ' angle out of range:' + str(angle))
        angle = abs(angle) if MOTOR_DEBUG_MODE else angle
        mapped_angle = int(self.map(angle) - self.pos0)
        mapped_angle = abs(mapped_angle) if MOTOR_DEBUG_MODE else mapped_angle
        serial_arg = 's' + str(self.motor) + self.mode
        if self.mode == 'a':
            serial_arg += str(mapped_angle)
        elif self.mode == 's':
            pulse = self._angle_to_pulse(mapped_angle)
            serialarg += str(pulse)
        self.port.write(serial_arg)
        if MOTOR_DEBUG_MODE:
            print angle, self.port.readline().strip()
        self.current_pos = angle

    def _angle_to_pulse(self, angle):
        """
        Converts angle linearly to pulse width.
        """
        return self.pwm[0] + (self.pwm[1] - self.pwm[0]) * angle / (self.range[1] - self.range[0])


def store_passes(satellite, outpath, n=100):
    data = satellite.next_passes(n)
    import csv
    keys = ['risetime', 'riseaz', 'maxtime', 'maxalt', 'settime', 'setaz']
    with open(outpath, 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


if __name__ == '__main__':
   interface.Server().start_server()
   raw_input('Interactive mode. Press enter to exit:  ')
