# SatTrack
Real time tracking of satellites

This code is for my engineering senior design project. The python class SatTrack is the main interface. It does the following things:
* Load satellite TLE data from file / parse web sources for it
* Track satellite position in real time
* Predict next pass (or next n passes)
* Connect to servo motors via serial port - arduino interface
* Visualize satellite position using a web interface implemented in D3js

An example of satellite tracking interface:  
![image](https://github.com/hazrmard/SatTrack/raw/master/demo.gif)

## Installation
1. Download/clone this repository,
2. In console, change directory to this repository,
3. Type:
```
python setup.py install
```
Note: python should previously be added to the system PATH variable. Otherwise the general instruction is:
```
<path to python.exe> <path to setup.py> install
```

External python dependencies are:
* [PyEphem](https://pypi.python.org/pypi/pyephem/)
* [lxml](https://pypi.python.org/pypi/lxml/3.5.0)
* [PySerial](https://pypi.python.org/pypi/pyserial)

For illustration the `test()` function in `test.py` contains basic uses of the SatTrack class.

##Usage
```python
from sattrack import SatTrack   # Import the `SatTrack` class:
s = SatTrack()                  # Instantiate class
s.set_location(lat='0', lon='0', ele=100)   # Set observer location
s.get_tle('satellite_name')     # Search CELESTRAK or AMSAT for satellite TLE data
s.load_tle('file_location')     # OR Load TLE from a file
s.begin_computing()             # Start calculating topocentric coordinates at 1 second intervals
s.show_location()               # Start printing satellite data to console
s.visualize()                   # Start a server and visualize satellite on map in browser
```
Class functions pertaining to servo motor control are still undergoing testing.  
For more details, see function definitions in the sourcecode.
