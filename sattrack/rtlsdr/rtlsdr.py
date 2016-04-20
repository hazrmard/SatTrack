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
        self.output = output
        self.freq = freq
        self.radio = None
        self.decoder = None

    def start_radio(self):
        self.radio = autoreceiver.AutoReceiver(freq=self.freq, file=self.output)

    def stop_radio(self, del_files=True):
        self.radio.terminate(del_files)

    def decode(self):
        self.decoder = autodecoder.AutoDecoder(self.output+'.wav')
        self.decoder.run()
