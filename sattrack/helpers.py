__author__ = 'Ibrahim'

import ephem
import re
from urlparse import urlparse
import requests
from dateutil import tz, parser

base_N2YO_URL =  'http://www.n2yo.com/satellite/?s=' 
base_CELESTRAK_URL = 'http://www.celestrak.com/NORAD/elements/'
CELESTRAK_paths = ('weather.txt', 'noaa.txt', 'goes.txt', 'resource.txt', 'sarsat.txt.', 'dmc.txt', 'tdrss.txt', 'argos.txt', 'geo.txt', 
                                'intelsat.txt', 'gorizont.txt', 'raduga.txt', 'molniya.txt', 'iridium.txt', 'orbcomm.txt', 'globalstar.txt',
                                'amateur.txt', 'x-comm.txt', 'other-comm.txt', 'gps-ops.txt', 'glo-ops.txt', 'galileo.txt', 'beidou.txt',
                                'sbas.txt', 'nnss.txt', 'musson.txt', 'science.txt', 'geodetic.txt', 'engineering.txt', 'education.txt', 'military.txt',
                                'radat.txt', 'cubesat.txt', 'other.txt',)
AMSAT_URL = 'http://www.amsat.org/amsat/ftp/keps/current/nasa.all'

def sanitize_url(url):
    return re.sub(r'\\', '/', url)


def parse_url(url):
    parsed = urlparse(url)
    try:
        id = re.search(r'^/(?P<id>[\w\-\._]+?)/.*', parsed.path).group('id')
    except AttributeError:
        id = None
    try:
        staticfile = re.search(r'/(?P<file>[\w\-\._]+?)$', parsed.path).group('file')
    except AttributeError:
        staticfile = None
    if parsed.query == '':
        query = None
    else:
        query = parsed.query
    return {'id': id, 'staticfile': staticfile, 'query': query}


def to_degs(rads):
    return rads * 180 / ephem.pi


def sanitize(string):
    return str(''.join([x for x in string if x.isalnum()]))


def tolocal(utc):       # takes ephem date object and returns localtime string
    return parser.parse(str(ephem.localtime(utc))).strftime('%Y-%m-%d %H:%M:%S')


def parse_text_tle(target, baseURL, extensions=('',)):
    #pattern = target + r'[\s)(]*?.*?[\n\r](.+?)[\n\r](.+?)[\n\r]'
    pattern = r'[\s]*?.*?' + target + r'[\t )(]*?.*?[\n\r\f\v]+?(.+?)[\n\r\f\v]+?(.+?)[\n\r\f\v]'
    for path in extensions:
        url = baseURL + path
        data = requests.get(url)
        match = re.search(pattern, data.text)
        if match:
            tle1 = match.group(1).strip()
            tle2 = match.group(2).strip()
            return (str(tle1), str(tle2))
        else:
            continue

'''
def parse_html_tle(baseURL=base_N2YO_URL, extensions=('',), xpath='//div/pre/text()'):
        for path in extensions:
            url = baseURL + path    
            page = requests.get(url)                # getting html data
            tree = html.fromstring(page.text)       # converting to tree format for parsing
            data = tree.xpath(xpath)   # remove all newline and whitespace
            data = data[0].rstrip().strip('\r').strip('\n')     # remove \r and \n
            data = data.splitlines()
            return data
 '''  