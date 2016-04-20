from sattrack import *

sattrack.MOTOR_DEBUG_MODE = True

# CONFIGURATION

def altmap(x):
    if x >= 82:
        return 0
    elif x<=0:
        return 130
    else:
        return 130. - x*(130./82.)

def altmap2(x):
    if x >= 90:
        return 40
    elif x<=0:
        return 175
    else:
        return 175. - x*(135./90.)

def altmap3(x):
    if x >= 90:
        return 180
    elif x<=0:
        return 60
    else:
        return 60. + (120./(90.))*(x+0.)

ALTRANGE = (0,90)
AZRANGE = (0, 360)
ALTMAP = altmap3
AZMAP = lambda x: 140.0 - (140.0/360.0)*x
INTERVAL = 1
MOTORS = (1,2)
TLEPATH = 'AO-85.tle'
PORT = None	# automatic port detection
PWM = (900, 2100)
TRACE = 0
TIMEOUT = 2
HOST = '0.0.0.0'

# END CONFIGURATION

def main():

    s = SatTrack()

    print 'Setting location.'
    s.set_location()

    print 'Loading TLE data.'
    s.load_tle(TLEPATH)
    print 'Satellite: ', s.id

    print 'Starting computing at interval: ' + str(INTERVAL) + 's.'
    s.begin_computing(interval=INTERVAL, trace=TRACE)
    s.visualize(openbrowser=False, host=HOST)

    print 'Connecting to servo motors.'
    s.connect_servos(port=PORT, minrange=(ALTRANGE[0], AZRANGE[0]), maxrange=(ALTRANGE[1], AZRANGE[1]), \
                                pwm=PWM, angle_map=(ALTMAP, AZMAP), timeout=TIMEOUT)
    print 'Test angle mapping: '
    print 'az.map(0):' + str(s.azmotor.map(0)), '\taz.map(360):' + str(s.azmotor.map(360))
    print 'alt.map(0): ' + str(s.altmotor.map(0)), '\talt.map(90): ' + str(s.altmotor.map(90))

    i = raw_input('Test calibration?[y/n]   ')
    if i=='y':
        print 'Moving azimuth to ' + str(AZRANGE[1])
        s.azmotor.move(AZRANGE[1])
        _ = raw_input('Press return to continue...');

        print 'Moving azimuth to ' + str(AZRANGE[0])
        s.azmotor.move(AZRANGE[0])
        _ = raw_input('Press return to continue...');

        print 'Moving altitude to ' + str(ALTRANGE[1])
        s.altmotor.move(ALTRANGE[1])
        _ = raw_input('Press return to continue...');

        print 'Moving altitude to ' + str(ALTRANGE[0])
        s.altmotor.move(ALTRANGE[0])
        _ = raw_input('Press return to continue...');

    print 'Finished connecting servos. Angle mapping complete.'

    i='n'
    while not i=='y':
        i = raw_input('Start tracking? [y/n]   ')
        if i =='n': break
    if i=='y':
        s.begin_tracking()

    i='n'
    while not i=='y':
        i = raw_input('Start receiving? [y/n]   ')
        if i =='n': break
    if i=='y':
        s.start_radio(output='AO85', freq='145.98M')

    i='n'
    while not i=='y':
        i = raw_input('Stop receiving? [y/n]   ')
    if i=='y':
        s.stop_radio()
        s.decode()

    raw_input('Press return to exit...')
    try:
        s.stop()
        s.serial.close()
    except:
        pass
    try:
        s.server.stop_server()
    except:
        pass



if __name__=='__main__':
    main()
