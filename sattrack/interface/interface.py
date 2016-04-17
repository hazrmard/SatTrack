__author__ = 'Ibrahim'

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json
import threading as th
import SimpleHTTPServer
import os
from ..helpers import *

DAEMON = True

class Server:
    '''This class maintains a single server thread across all instances of SatTrack.
    If a server is already running, and start_server(new=False) then does nothing.
    Else for the first instance or when new=True, creates a new server thread.
    '''
    isServing = False
    server = None           # single server shared by all instances of SatTrack
    server_thread = None    # single thread shared by all instances of SatTrack
    stop = th.Event()       # event that signals server thread to terminate

    def __init__(self):
        #self.server_thread = th.Thread(target=self._serve)
        #self.stop = th.Event()
        self.host = None
        self.port = None

    def start_server(self, host='localhost', port=8000, new=False):
        if new and Server.isServing:
            self.stop_server()
        elif not new and Server.isServing:
            return
        self.server_thread = th.Thread(target=self._serve)
        Server.server = HTTPServer((host, port), Interface)
        self.serve()
        Server.isServing = True
        self.host = host
        self.port = port

    def add_source(self, src):
        Interface.sources[src.id] = src

    def remove_source(self, src):
        try:
            del Interface.sources[src.id]
        except KeyError:
            pass

    def serve(self):
        Server.server_thread = self.server_thread
        Server.server_thread.daemon = DAEMON
        Server.server_thread.start()

    def _serve(self):
        while not Server.stop.isSet():
            Server.server.handle_request()
        print 'STOP SERVER SET'

    def stop_server(self):
        #Server.server.shutdown()
        Server.stop.set()
        Server.server.server_close()
        Server.server_thread.join(timeout=1)
        Server.stop.clear()
        Server.server_thread = None
        #print 'Server thread alive? ', Server,server_thread.isAlive()
        Server.isServing = False
        Server.server = None


class Interface(SimpleHTTPServer.SimpleHTTPRequestHandler):

    sources = {}
    localpath = sanitize_url(os.path.dirname(__file__)) + '/'

    def do_GET(self):
        """
        This function handles GET requests made by the client. The general URL is of the format:
            http://localhost:PORT/SATELLITE_ID/?QUERY
        :return:
        """
        source = None
        localpath = Interface.localpath
        parsed = parse_url(self.path)
        if parsed['path'] == '/' and parsed['query'] is not None:
            from ..sattrack import SatTrack # python prevents repetitive imports
            satellite = populate_class_from_query(SatTrack(), parsed['query'])
            Interface.sources[satellite.id] = satellite
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(satellite.id)
            return
        elif self.path == '/' and parsed['query'] is None:  # i.e. localhost:port_number/
            self.path = localpath + 'dashboard.html'      # set entry point
            #print '\npath modified to: ' + self.path
        else:                                             # serve satellite page / query
            if parsed['id']:                                # i.e. localhost:port_number/valid_id/
                if parsed['id'] in Interface.sources:
                    source = Interface.sources[parsed['id']]
                if not parsed['query']:                     # if GET request is not a JSON query then continue page loading
                    self.path = localpath
            if parsed['staticfile']:                        # i.e. some_path/script.js (as referenced in index.html)
                if parsed['staticfile'] in os.listdir(os.path.dirname(__file__)):
                    self.path = localpath + parsed['staticfile']
                    #print '\nstatic file requested: ' + self.path
                else:
                    self.send_response(400, 'File not found: ' + parsed['staticfile'])
                    return
            if parsed['query'] and source:                             # handle any queries
                if parsed['query'] == u'status' and source:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(self.genJSON(source))
                elif parsed['query'] == u'stopcomputing':
                    self.send_response(200)
                    source.stop_computing()
                elif parsed['query'] == u'stoptracking':
                    self.send_response(200)
                    source.stop_tracking()
                elif parsed['query'] == u'startcomputing':
                    self.send_response(200)
                    source.begin_computing()
                elif parsed['query'] == u'starttracking':
                    self.send_response(200)
                    source.begin_tracking()
                else:
                    self.send_response(400, 'Source not found.')
                return      # quit after returning json

        SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


    def genJSON(self, source):
        d = {}
        d['lon'] = to_degs(source.satellite.sublong)
        d['lat'] = to_degs(source.satellite.sublat)
        d['az'] = to_degs(source.satellite.az)
        d['alt'] = to_degs(source.satellite.alt)
        d['interval'] = source.default_config['interval']
        d['time'] = str(source.observer.date)
        d['log'] = source.get_log()
        return json.dumps(d)

    def log_message(self, format, *args):   # override to silence console output
        return None


def main():
    Server().start_server()


def debug():
    print os.path.dirname(__file__)
    print os.listdir(os.path.dirname(__file__))
    print __file__

if __name__=='__main__':
    import sys
    print os.path.dirname(__file__)
    sys.path.append(os.path.dirname(__file__))
    p = th.Thread(target=main)
    p.start()
    i=''
    while i!='exit':
        i = raw_input("Enter 'exit' to stop server:   ")
    p.join(timeout=1)
