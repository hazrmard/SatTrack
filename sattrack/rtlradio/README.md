#RTL-SDR
Signal reception module for SatTrack
  
##Requirements
These requirements are not final. They currently represent all I have done to get rtl-sdr working on different systems. The final set of requirements may be shorter.

###Linux
* [pyrtlsdr](http://github.com/roger-/pyrtlsdr)  
* [rtl-sdr](http://sdr.osmocom.org/trac/blog/rtl-sdr-introduction)
```
$ sudo apt-get rtl-sdr
```
  
###Windows
* [pyrtlsdr](http://github.com/roger-/pyrtlsdr)  
* [rtl-sdr drivers](http://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)
* [librtlsdr for windows](http://sdr.osmocom.org/trac/attachment/wiki/rtl-sdr/RelWithDebInfo.zip)
  
`pyrtlsdr` can also be installed from pip:
```
$ pip install pyrtlsdr
```
All files in `librtlsdr` (either 32 bit or 64 bit directories, same as python version) should either be in system PATH or in the same directory as pyrtlsdr.


