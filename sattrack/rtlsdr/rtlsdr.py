try:
    import autoreceiver
    import autodecoder
    STATUS = 1
except ImportError:
    STATUS = -1
    print 'AutoDecoder and/or AutoReceiver packages not installed.'
    print 'Please install from: https://github.com/hazrmard/SDR_flow_automation,'
    print 'OR: add rtl-sdr, java, and sox to system path variable.'

class RtlSdr:

    def __init__(self, freq, output):
        self.output = output        #output file name, NO extension
        self.freq = freq            #string frequency e.g. '145.98M'
        self.radio = None           #autoreceiver.AutoReceiver()
        self.decoder = None         #autodecoder.AutoDecoder()

    def start_radio(self):
        '''immediately spawns a process that listens and stores frequency in a
        bin file.
        '''
        self.radio = autoreceiver.AutoReceiver(freq=self.freq, file=self.output)

    def stop_radio(self, del_files=True):
        '''teminates listening process and converts to wav file using sox package
        :del_files: delete intermediate files
        '''
        self.radio.terminate(del_files)

    def decode(self):
        '''calls a python wrapper for AMSAT Fox Telem package to decode data.
        spacecraft folder containing satellite data should be in the working directory.
        '''
        self.decoder = autodecoder.AutoDecoder(self.output+'.wav')
        self.decoder.run()
