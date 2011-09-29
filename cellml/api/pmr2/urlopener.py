import urllib2
import urlparse

import zope.interface
from zope.schema.fieldproperty import FieldProperty

from cellml.api.pmr2.interfaces import IURLOpener
from cellml.api.pmr2.interfaces import UnapprovedProtocolError


class BaseURLOpener(object):
    """\
    The base URL Opener.
    """

    zope.interface.implements(IURLOpener)

    approved_protocol = FieldProperty(IURLOpener['approved_protocol'])

    def validateProtocol(self, location):
        raise NotImplementedError

    def loadURL(self, location):
        raise NotImplementedError

    def __call__(self, location):
        if not self.validateProtocol(location):
            raise UnapprovedProtocolError(
                'protocol for the location is not approved')
        return self.loadURL(location)


class DefaultURLOpener(BaseURLOpener):
    """\
    Default implementation of the URL opener.
    """

    def __init__(self):
        self.approved_protocol = ['http', 'https',]

    def validateProtocol(self, location):
        return urlparse.urlparse(location).scheme in self.approved_protocol

    def loadURL(self, location, headers=None):
        request = urllib2.Request(location)
        request.add_header('User-agent', 
            # XXX temporary user agent header
            'cellml.api.pmr2/0.0 (http://models.cellml.org/;)')

        if headers:
            for k, v in headers:
                request.add_header(k, v)

        response = urllib2.urlopen(request)
        result = response.read()
        response.close()
        return result
