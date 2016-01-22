__author__ = 'Ibrahim'

from sattrack import *


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
    #s.get_tle(40967)
    #print s.next_pass()
    s.begin_computing(interval=1, trace=0)  # trace > 0 speeds up by a factor of trace / interval (otherwise realtime)
    #s.connect_servos(minrange=(10, 10), maxrange=(170, 170))
    #s.begin_tracking()
    s.visualize()
    #s.show_position()
    # print 'Front end server set up...'
    # i = input('Exit? ... ')
    # if i =='y':
    #     s.server.stop_server()
    # print 'server closed'
    # return s


def q():
    try:
        Server().stop_server()
        print "Server closed."
    except:
        "Server already closed"
    reload(sattrack)
    print '\nsattrack reloaded...'
