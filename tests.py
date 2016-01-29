import unittest
from sattrack import SatTrack
from sattrack.interface import Server
from sattrack.helpers import *
import ephem

class HelpersTest(unittest.TestCase):
    def test_to_degs(self):
        self.assertAlmostEqual(to_degs(ephem.pi), 180.0)

class SatTrackTest(unittest.TestCase):
    def setUp(self):
        self.s = SatTrack()
    
    def test_set_location(self):
        self.s.set_location(lat='36.1486', lon='-86.8050', ele=182)
        self.assertAlmostEqual(to_degs(self.s.observer.lat), 36.1486)
        self.assertAlmostEqual(to_degs(self.s.observer.lon), -86.8050)
        self.assertEqual(self.s.observer.elev, 182)
    
    def test_get_tle(self):     # also tests internet connection
        res = self.s.get_tle('AO-85')
        self.assertTrue(isinstance(res, tuple) and len(res)==2)
    
    def test_begin_computing(self):
        self.s.begin_computing()
        self.assertTrue('tracker' in self.s.threads and self.s.threads['tracker'].isAlive())
    
    def test_visualize(self):
        self.s.visualize(openbrowser=False)
        self.assertTrue(Server.isServing and Server.server_thread.isAlive())
    
    def tearDown(self):
        pass


if __name__ == 'main':
    print 'Begin test'
    unittest.main()