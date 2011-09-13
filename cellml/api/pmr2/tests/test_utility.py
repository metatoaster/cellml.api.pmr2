import unittest
from lxml import etree
from cStringIO import StringIO
from os.path import basename, dirname, join
import urllib2
from urlparse import urljoin

from cellml.api.pmr2.utility import CellMLAPIUtility


base = dirname(__file__)
input_p = 'input'
# XXX not tested on Windows...
get_path = lambda *p: urljoin('file://', join(base, input_p, *p))


class CustomCellMLAPIUtility(CellMLAPIUtility):
    def loadURL(self, location):
        """
        Allow a stream object to be passed as a location
        """

        if hasattr(location, 'read'):
            return location.read()
        else:
            return CellMLAPIUtility.loadURL(self, location)

    # loadModel should not need redefining as the stream object should
    # be replaced by the xml:base in test_0111.


class UtilityTestCase(unittest.TestCase):

    def setUp(self):
        self.utility = CellMLAPIUtility()
        self.utility.approved_protocol.append('file')

    def tearDown(self):
        pass

    def assertComponentName(self, componentSet, name):
        comp = componentSet.getComponent(name)
        self.assertEqual(comp.getname(), name)

    def test_0000_basic(self):
        self.assert_(self.utility.cellml_bootstrap)

    def test_0100_model_load_standard(self):
        model_path = get_path('beeler_reuter_model_1977.cellml')
        model = self.utility.loadModel(model_path)
        self.assertEqual(model.getcmetaId(), 
            'beeler_reuter_mammalian_ventricle_1977')

    def test_0110_model_load_imported(self):
        model_path = get_path('subdir1', 'subdir2', 'toplevel.xml')
        tl = self.utility.loadModel(model_path)
        v1 = tl.getimports().iterateImports().nextImport().getimportedModel()
        v2 = v1.getimports().iterateImports().nextImport().getimportedModel()
        self.assertComponentName(tl.getmodelComponents(), 'toplevel_component')
        self.assertComponentName(v1.getmodelComponents(), 'level1_component')
        self.assertComponentName(v2.getmodelComponents(), 'level2_component')

    def test_0111_model_load_imported(self):
        model_path = get_path('subdir1', 'subdir2', 'toplevel.xml')
        fd = urllib2.urlopen(model_path)
        doc = etree.parse(fd)
        fd.close()
        doc.getroot().set('{http://www.w3.org/XML/1998/namespace}base', 
            model_path)
        stream = StringIO(etree.tostring(doc))
        # add the above as xmlbase into new file in temporary location
        utility = CustomCellMLAPIUtility()
        tl = utility.loadModel(stream)
        v1 = tl.getimports().iterateImports().nextImport().getimportedModel()
        v2 = v1.getimports().iterateImports().nextImport().getimportedModel()
        self.assertComponentName(tl.getmodelComponents(), 'toplevel_component')
        self.assertComponentName(v1.getmodelComponents(), 'level1_component')
        self.assertComponentName(v2.getmodelComponents(), 'level2_component')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilityTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
