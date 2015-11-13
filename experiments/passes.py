__author__ = 'Ibrahim'

import ephem as ep
from datetime import datetime


row1 = 'FOX1A'
row2 = '1 40967U 15058D   15302.30036689  .00001904  00000-0  21334-3 0 00240'
row3 = '2 40967 064.7795 228.7545 0217878 275.5719 236.2101 14.74335309002925'


def test():
    obs = ep.Observer()
    obs.lon = '-86.805'
    obs.lat = '36.1486'
    obs.elev = 186
    obs.epoch = ep.Date(str(datetime.utcnow()))
    obs.date = ep.Date(str(datetime.utcnow()))

    for i in range(10):
        sat = ep.readtle(row1, row2, row3)
        sat.compute(obs)
        n = obs.next_pass(sat)
        print str(n[4])
        obs.date = ep.Date(n[4] + ep.minute)
