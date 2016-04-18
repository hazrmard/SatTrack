from sattrack import *

if __name__ == '__main__':
   interface.Server().start_server(host='0.0.0.0')
   raw_input('Interactive mode. Press enter to exit:  ')
