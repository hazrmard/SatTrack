# SatTrack
Real time tracking of satellites

This code is for my engineering senior design project. The python class SatTrack is the main interface. It does the following things:
* Load satellite TLE data from file / parse web sources for it
* Track satellite position in real or sped up time
* Predict next pass (or next n passes)
* Controll antenna using servo motors via serial port - arduino interface
* Visualize satellite position using a web interface implemented in D3js
* Access the GUI on a mobile/remote device over wifi
* Record transmissions at a particular frequency using RTL SDR.

An example of satellite tracking interface:  
![image](https://github.com/hazrmard/SatTrack/raw/interface_cleanup/demo.gif)

## Requirements

### Basic
* Python 2.7
* A modern web browser (only for visualization)  

### Antenna control
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
* [PySerial](https://pypi.python.org/pypi/pyserial) (for connecting to Arduino)
* [Requests](https://pypi.python.org/pypi/requests) (for downloading satellite data)
* [Dateutil](https://pypi.python.org/pypi/python-dateutil)
* [SDR_flow_automation](https://github.com/hazrmard/SDR_flow_automation) (for using RTL software defined radio)

For illustration the `sandbox.py` and `trial.py` which contain basic uses of the SatTrack class.

## Usage  
## Easy Way  
The easy way is a GUI in a web browser. After installing SatTrack, type:
```bash
> python -m sattrack.interactive
```  
The GUI simplifies controls by requiring less arguments. The values put in `defaults.py` are used for all satellite instances created.  
This starts a local server on `localhost:8000` and also broadcasts it over the device's network. You can open up the interface by typing `localhost:8000` on your local browser. Or you can access the interface from any web browser on another device by going to `<HOST_IP_ADDRESS>:8000` e.g `192.168.42.1:8000`. For connecting servos etc. see *Set up* and *Wiring* in the next section.  

## Hard Way  

### Tracking Satellites
```python
from sattrack import SatTrack   # Import the `SatTrack` class:
s = SatTrack()                  # Instantiate class
s.set_location(lat='0', lon='0', ele=100)   # Set observer location
s.get_tle('satellite_name')     # Search CELESTRAK or AMSAT for satellite TLE data
s.load_tle('file_location')     # OR Load TLE from a file. get_tle() and load_tle() create the satellite to track.
s.begin_computing()             # Start calculating topocentric coordinates at 1 second intervals.
s.visualize()                   # Start a server and visualize satellite on map in browser
```
Check [AMSAT](http://www.amsat.org/amsat/ftp/keps/current/nasa.all) and [CELESTRAK](http://www.celestrak.com/NORAD/elements/) for satellite names.  The TLE format SatTrack accepts can be seen in `AO-85.tle`.  

### Servo Control
This functionality was added to allow antennas to track a satellite's pass using 2 servo motors. One servo motor controls azimuth and the other controls altitude.  
Servo control is split into 2 parts: getting coordinates for satellite, and conveying them to servo motors.

#### Set up
1. Connect an arduino board via a USB port to the computer.
2. Load the file `ServoCont/multipleSerialServoControl/multipleSerialServoControl.ino` onto the board.
3. Quit the arduino IDE to free up USB port control.
For most servo motors, you will not need to make any changes to the `.ino` file.

#### Wiring
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

#### Connecting SatTrack
After the satellite TLE data has been retrieved, observer location is set, and position calculations have begun,
```python
# continuing from SatTrack instance 's'
s.connect_servos(port='COM3', motors=(1,2), minrange(0,0), maxrange=(90,360), \
                  angle_map=(lambda x:x, lambda x:x), pwm=(900,2100), timeout=1)   
# All tuples have parameters for (altitude servo, azimuth servo)
# --angle_map is a tuple of functions that takes in the aititude/azimuth angle (degrees)
#   and modifies it according to antenna position (e.g if it is on a slope etc.).
# --pwm is a tuple containing minimum and maximum pulse widths that are used to control
#   the servos.
s.begin_tracking()
```  
*Note:* In case of empty/None parameters, default values in `defaults.py` are used.  
And that's it!
  
### Listening in  
`SatTrack` comes with a basic interface to use RTL software defined radios. Before using this, the [SDR_flow_automation](https://github.com/hazrmard/SDR_flow_automation) dependency needs to be installed and `java`, `sox`, and `rtl-sdr` need to be added to the system path. More instructions can be found on the repository page. After that:  
```python
s.start_radio('freq', 'output_file')      # e.g freq='123M' for 123 MHz
_ = raw_input("Press any key to stop...") # any duration to record
s.stop_radio()
```
Output is stored as a `.wav` file.

### Clean up
```python
s.stop()                # stop computations and tracking
s.server.stop_server()  # stop server in case you are visualizing satellite
```

Class functions pertaining to servo motor control are still undergoing testing.  
For more details, see function definitions in the sourcecode.  
For examples, see `sandbox.py`.

