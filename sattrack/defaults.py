# Default values for parameters
from helpers import find_arduino

lat = 36.1486
lon = -86.8050
ele = 182

interval = 1.0
trace = 0.0

port = find_arduino()
motors = (1,2)
minrange = (0, 0)
maxrange = (90, 360)
initpos = (0, 0)
angle_map = (lambda x: x, lambda x: x)
timeout = 2
baudrate = 9600
pwm = (900, 2100)

host = '0.0.0.0'
