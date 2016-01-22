__author__ = 'Ibrahim'

import re
from urlparse import urlparse


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
