__author__ = 'Ibrahim'

from sattrack import *
import time

sattrack.MOTOR_DEBUG_MODE = True


def test(tlepath='fox1.tle'):
    s = SatTrack()
    s.set_location()
    s.load_tle(tlepath)
    #s.get_tle(40967)
    print s.next_pass()
    s.begin_computing(interval=1, trace=0)  # trace > 0 speeds up by a factor of trace / interval (otherwise realtime)
    #s.connect_servos(minrange=(10, 10), maxrange=(170, 170))
    #s.begin_tracking()
    #s.visualize()
    s.show_position()
    # print 'Front end server set up...'
    # i = input('Exit? ... ')
    # if i =='y':
    #     s.server.stop_server()
    # print 'server closed'
    return s
    
def test_web(tlepath='fox1.tle'):
    s = SatTrack()
    s.set_location()
    s.load_tle(tlepath)
    s.begin_computing(interval=1, trace=0)  # trace > 0 speeds up by a factor of trace / interval (otherwise realtime)
    s.visualize()
    return s


def test_tracking(name='AO-85', port='COM3'):
    s = SatTrack()
    s.set_location()
    s.get_tle(name)
    s.begin_computing(interval=1, trace=10)
    s.connect_servos(port, minrange=(-90, 0), maxrange=(90, 360))
    s.begin_tracking()
    s.visualize()
    return s


def motor_test(num, interval):
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
    

def q():
    try:
        Server().stop_server()
        print "Server closed."
    except:
        "Server already closed"
