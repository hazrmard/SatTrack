__author__ = 'Ibrahim'

import ephem
from datetime import datetime

class SatTrack:
    def __init__(self, lat=36.1486, lon=-86.8050, ele=182):
        self.latitude = lat
        self.longitide = lon
        self.elevation = ele
        self.observer = ephem.Observer()
        self._configure_observer()

    def _configure_observer(self):
        self.observer.lat = self.latitude
        self.observer.lon = self.longitide
        self.observer.elev = self.elevation
        self.observer.date = datetime.utcnow()