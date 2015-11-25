# SatTrack
Real time tracking of satellites

This code is for my engineering senior design project. The python class SatTrack is the main interface. It does the following things:
* Load satellite TLE data from file / parse web sources for it
* Track satellite position in real time
* Predict next pass (or next n passes)
* Connect to servo motors via serial port - arduino interface
* Visualize satellite position using a web interface implemented in D3js

This project is still in development and has not been packaged for quick installation.

External python dependencies are:
* [PyEphem](https://pypi.python.org/pypi/pyephem/)
* [lxml](https://pypi.python.org/pypi/lxml/3.5.0)
* [PySerial](https://pypi.python.org/pypi/pyserial)

For illustration the `test()` function in `sattrack.py` contains basic uses of the SatTrack class.
