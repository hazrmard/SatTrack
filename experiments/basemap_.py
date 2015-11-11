__author__ = 'Ibrahim'

from mpl_toolkits.basemap import Basemap
from matplotlib.pyplot import figure, ion, draw, show
import numpy as np
import  time

f = figure(1)

m = Basemap(projection='geos',lon_0=0,resolution='l')
m.drawcoastlines()
m.fillcontinents(color='coral',lake_color='aqua')
# draw parallels and meridians.
m.drawparallels(np.arange(-90.,120.,30.))
m.drawmeridians(np.arange(0.,420.,60.))
m.drawmapboundary(fill_color='aqua')

x = [10, 14, 20, 30]
y = [0, 10, 15, 40]
x, y = m(x,y)
d, =m.plot(x,y)

ion()
show(f)

# for i in range(10):
#     px, py = m(x[-1]-5, y[-1]-3)
#     x += [px]
#     y += [py]
#     d.set_xdata(x)
#     d.set_ydata(y)
#     f.draw()
#     time.sleep(0.5)

