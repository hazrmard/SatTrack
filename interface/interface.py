__author__ = 'Ibrahim'

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import json
import threading as th
import SimpleHTTPServer
import re
import os


class Server:
    isServing = False
    server = None
    server_thread = None
    stop = th.Event()

    def __init__(self):
        self.server_thread = th.Thread(target=self._serve)
        self.stop = th.Event()
        self.host = None
        self.port = None

    def start_server(self, host='localhost', port=8000, new=False):
        if new and Server.isServing:
            self.stop_server()
        elif not new and Server.isServing:
            return
        Server.server = HTTPServer((host, port), Interface)
        self.serve()
        Server.isServing = True
        self.host = host
        self.port = port

    def add_source(self, src):
        Interface.sources[src.id] = src

    def serve(self):
        self.server_thread.daemon = True
        Server.server_thread = self.server_thread
        Server.server_thread.start()

    def _serve(self):
        while not Server.stop.isSet():
            Server.server.handle_request()

    def stop_server(self):
        Server.stop.set()
        Server.server_thread.join(timeout=1)
        Server.server.server_close()
        Server.isServing = False


class Interface(SimpleHTTPServer.SimpleHTTPRequestHandler):

    sources = {}

    def do_GET(self):
        """
        This function handles GET requests made by the client. The general URL is of the format:
            http://localhost:PORT/SATELLITE_ID?QUERY
        :return:
        """
        parsed_path = urlparse.urlparse(self.path)
        path = re.split(r'/|\\', parsed_path[2])
        path = [x for x in path if x != '']     # isolate path to find which satellite to use as source
        # print Interface.sources.keys()
        if len(path) == 0:          # i.e no path given, set it to 'interface' to get index.html
            self.path = os.path.dirname(__file__) + '/'
        elif len(path) > 0:
            if os.path.isdir('interface') and path[0] in os.listdir('interface'):   # path given is an actual file
                # print 'requesting file'
                self.path = os.path.dirname(__file__) + '/' + unicode(path[0])   # set path to the file
            else:   # path is not a file and is not empty -> should be SATELLITE_ID
                # print 'SAT ID provided in URL:', path[0]
                try:
                    source = Interface.sources[path[0]]
                    # print 'Source found.'
                except KeyError as e:
                    print 'ID not found:', e.message
                self.path = os.path.dirname(__file__) + '/'  # load the original page
        if parsed_path.query == u'status':
            # print 'request validated:', path[0]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.genJSON(source)))
            return      # quit after returning json
        return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def genJSON(self, source):
        d = {}
        d['lon'] = source.satellite.sublong * 180 / 3.14
        d['lat'] = source.satellite.sublat * 180/ 3.14
        d['az'] = source.satellite.alt * 180/ 3.14
        d['alt'] = source.satellite.alt * 180/ 3.14
        d['interval'] = source.interval
        d['time'] = str(source.observer.date)
        return d

    def log_message(self, format, *args):   # override to silence console output
        return


def main():
    s = Server()
    s.start_server()
    i = input('Exit? ... ')
    if i =='y':
        s.stop_server()
    print 'server closed'



