__author__ = 'Ibrahim'

from sattrack import *
import time

sattrack.MOTOR_DEBUG_MODE = True

# Motor specific configuration
ALTMAP = lambda x: 15 + (105-15) * x / 90      # mapping 0-90 to 20-95
AZMAP = lambda x: 47 + (143-47) * x / 360     #  mapping 0-360 to 47-143

def test(tlepath='fox1.tle'):
    s = SatTrack()
    s.set_location()
    s.load_tle(tlepath)
    print s.next_pass()
    s.begin_computing(interval=1, trace=0)  # trace > 0 speeds up by a factor of trace / interval (otherwise realtime)
    s.show_position()
    return s
    
def test_web(tlepath='fox1.tle'):
    s = SatTrack()
    s.set_location()
    s.load_tle(tlepath)
    s.begin_computing(interval=1, trace=10)  # trace > 0 speeds up by a factor of trace / interval (otherwise realtime)
    s.visualize()
    return s


def test_tracking(name='AO-85', port='COM3'):
    s = SatTrack()
    s.set_location()
    s.get_tle(name)
    s.begin_computing(interval=1, trace=10)
    s.connect_servos(port, minrange=(0, 0), maxrange=(90, 360))
    s.altmotor.map = ALTMAP
    s.azmotor.map = AZMAP
    s.begin_tracking()
    s.visualize()
    return s


def test_motor(num, interval):
    servos = ServoController(port='COM3', motors=(1,2))
    altmotor, azmotor = servos.motors
    altmotor.map = lambda x: 15 + (105-15) * x / 90      # mapping 0-90 to 20-95
    for i in range(0, 91):
        if num==1:
            altmotor.move(i)
        elif num==2:
            azmotor.move(i)
        time.sleep(interval)
# Azimuth motor has limits (47->143) => (-90->270)
    

def q(s=None):
    if s:
        s.stop()
    try:
        Server().stop_server()
        print "Server closed."
    except:
        "Server already closed"
