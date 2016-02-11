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

##Requirements

###Basic
* Python 2.7
* A modern web browser (only for visualization)  

###Antenna control
* Arduino Uno (Board and IDE)
* 2 x servos
* 5-7V DC power supply

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
* [Requests](https://pypi.python.org/pypi/requests)

For illustration the `test()` function in `test.py` contains basic uses of the SatTrack class.

##Usage
###Tracking Satellites
```python
from sattrack import SatTrack   # Import the `SatTrack` class:
s = SatTrack()                  # Instantiate class
s.set_location(lat='0', lon='0', ele=100)   # Set observer location
s.get_tle('satellite_name')     # Search CELESTRAK or AMSAT for satellite TLE data
s.load_tle('file_location')     # OR Load TLE from a file. get_tle() and load_tle() create the satellite to track.
s.begin_computing()             # Start calculating topocentric coordinates at 1 second intervals.
s.show_location()               # Start printing satellite data to console
s.visualize()                   # Start a server and visualize satellite on map in browser
```
Check [AMSAT](http://www.amsat.org/amsat/ftp/keps/current/nasa.all) and [CELESTRAK](http://www.celestrak.com/NORAD/elements/) for satellite names.  The TLE format SatTrack accepts can be seen in `fox1.tle`.  
###Servo Control
This functionality was added to allow antennas to track a satellite's pass using 2 servo motors. One servo motor controls azimuth and the other controls altitude.  
Servo control is split into 2 parts: getting coordinates for satellite, and conveying them to servo motors.
####Set up
1. Connect an arduino board via a USB port to the computer. You should know the name of the port e.g. `COM3`.
2. Load the file `ServoCont/multipleSerialServoControl/multipleSerialServoControl.ino` onto the board.
3. Quit the arduino IDE to free up USB port control.
For most servo motors, you will not need to make any changes to the `.ino` file.

####Wiring
Each servo motor is has 3 wire connections:
* Voltage High (usually red)
* Ground (usually black)
* Control (usually yellow)
To protect arduino'c circuitry, connect the power supply wires to an external power source. Make sure that the ground connections are tied: both ground pins (on the arduino and the servo motors) are on the same node.  

The arduino is programmed to control up to 6 servo motors. The pin assignments for control wires are:  

| Motor \# | Pin |  
| --- | --- |  
| 1 | 9 |  
| 2 | 3 |  
| 3 | 4 |  
| 4 | 5 |  
| 5 | 10 |  
| 6 | 11 |  

####Connecting SatTrack
After the satellite TLE data has been retrieved, observer location is set, and position calculations have begun,
```python
# continuing from SatTrack instance 's'
s.connect_servos(port='COM3', motors=(1,2), minrange(0,0), maxrange=(90,360))   # (altitude servo, azimuth servo)
s.begin_tracking()
```
And that's it!

###Clean up
```python
s.stop()                # stop computations and tracking
s.server.stop_server()  # stop server in case you are visualizing satellite
```

Class functions pertaining to servo motor control are still undergoing testing.  
For more details, see function definitions in the sourcecode.  
For examples, see `sandbox.py`.

