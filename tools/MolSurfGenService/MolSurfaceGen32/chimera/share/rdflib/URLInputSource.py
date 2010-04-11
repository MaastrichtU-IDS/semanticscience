from urllib2 import urlopen, Request

from xml.sax.xmlreader import InputSource

from rdflib import __version__

# TODO: add types for n3. text/rdf+n3 ?
headers = {
    'Accept': 'application/rdf+xml,application/xhtml+xml;q=0.5',
    'User-agent':
    'rdflib-%s (http://rdflib.net/; eikeon@eikeon.com)' % __version__
    }


class URLInputSource(InputSource, object):
    def __init__(self, system_id=None):
        super(URLInputSource, self).__init__(system_id)
        self.url = system_id
        # So that we send the headers we want to...
        req = Request(system_id, None, headers)
        file = urlopen(req)
        self.setByteStream(file)
        # TODO: self.setEncoding(encoding)

    def __repr__(self):
        return self.url
