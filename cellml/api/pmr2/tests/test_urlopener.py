import unittest
from lxml import etree
from cStringIO import StringIO
from os.path import basename, dirname, join
import urllib2
from urlparse import urljoin

from cellml.api.pmr2.interfaces import UnapprovedProtocolError
from cellml.api.pmr2.urlopener import BaseURLOpener
from cellml.api.pmr2.urlopener import DefaultURLOpener


class URLOpenerTestCase(unittest.TestCase):

    def setUp(self):
        self.opener = DefaultURLOpener()

    def tearDown(self):
        pass

    def test_0000_basic(self):
        opener = BaseURLOpener()
        # please fail
        self.assertRaises(NotImplementedError, opener, 'fail')

    def test_0100_badprotocol(self):
        fileurl = 'file:///'
        self.assertRaises(UnapprovedProtocolError, self.opener, fileurl)

    # testcases for successful invocations will be left for the ones
    # that integrate this class.


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(URLOpenerTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
