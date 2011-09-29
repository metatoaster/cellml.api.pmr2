import unittest
from lxml import etree
from cStringIO import StringIO
from os.path import basename, dirname, join
import urllib2
from urlparse import urljoin

from cellml.api.pmr2.interfaces import UnapprovedProtocolError
from cellml.api.pmr2.utility import CellMLAPIUtility
from cellml.api.pmr2.utility import DefaultURLOpener
from cellml_api import CellML_APISPEC


base = dirname(__file__)
input_p = 'input'
# XXX not tested on Windows...
get_path = lambda *p: urljoin('file://', join(base, input_p, *p))


class StreamURLOpener(DefaultURLOpener):
    """
    Allow a stream object to be passed as a location, and it is treated
    as a valid protocol and is loaded via reading itself.
    """

    def validateProtocol(self, location):
        if hasattr(location, 'read'):
            return True
        return DefaultURLOpener.validateProtocol(self, location)

    def loadURL(self, location):
        if hasattr(location, 'read'):
            return location.read()
        return DefaultURLOpener.loadURL(self, location)


class UtilityTestCase(unittest.TestCase):

    def setUp(self):
        self.utility = CellMLAPIUtility()
        self.opener = StreamURLOpener()
        self.opener.approved_protocol.append('file')

    def tearDown(self):
        pass

    def assertComponentName(self, componentSet, name):
        comp = componentSet.getComponent(name)
        self.assertEqual(comp.getname(), name)

    def test_0000_basic(self):
        self.assert_(self.utility.cellml_bootstrap)

    def test_0010_model_load_file_fail(self):
        model_path = get_path('beeler_reuter_1977-api-test.cellml')
        # default loader will not allow file://
        self.assertRaises(UnapprovedProtocolError,
                          self.utility.loadModel, model_path)

    def test_0100_model_load_standard(self):
        model_path = get_path('beeler_reuter_1977-api-test.cellml')
        model = self.utility.loadModel(model_path, self.opener)
        self.assertEqual(model.getcmetaId(), 
            'beeler_reuter_mammalian_ventricle_1977')

    def test_0110_model_load_imported(self):
        model_path = get_path('subdir1', 'subdir2', 'toplevel.xml')
        tl = self.utility.loadModel(model_path, self.opener)
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
        # add the above as xmlbase into new file in temporary location
        doc.getroot().set('{http://www.w3.org/XML/1998/namespace}base', 
            model_path)
        stream = StringIO(etree.tostring(doc))
        # use the custom utility with the modified loader
        tl = self.utility.loadModel(stream, self.opener)
        v1 = tl.getimports().iterateImports().nextImport().getimportedModel()
        v2 = v1.getimports().iterateImports().nextImport().getimportedModel()
        self.assertComponentName(tl.getmodelComponents(), 'toplevel_component')
        self.assertComponentName(v1.getmodelComponents(), 'level1_component')
        self.assertComponentName(v2.getmodelComponents(), 'level2_component')

    def test_0112_model_load_multiple_import(self):
        model_path = get_path('multiimport.xml')
        fd = urllib2.urlopen(model_path)
        doc = etree.parse(fd)
        fd.close()
        # add the above as xmlbase into new file in temporary location
        doc.getroot().set('{http://www.w3.org/XML/1998/namespace}base', 
            model_path)
        stream = StringIO(etree.tostring(doc))
        # use the custom utility with the modified loader
        tl = self.utility.loadModel(stream, self.opener)
        isi = tl.getimports().iterateImports()
        v1 = isi.nextImport().getimportedModel()
        v2 = isi.nextImport().getimportedModel()

        self.assertComponentName(tl.getmodelComponents(), 'component1')
        self.assertComponentName(tl.getmodelComponents(), 'component2')

        self.assertComponentName(v1.getmodelComponents(), 'level1_component')
        self.assertComponentName(v2.getmodelComponents(), 'level2_component')

    def test_0200_model_load_broken(self):
        model_path = get_path('broken_xml.cellml')
        self.assertRaises(CellML_APISPEC.CellMLException,
                          self.utility.loadModel, model_path, self.opener)
        lastmsg = self.utility.model_loader.getlastErrorMessage()
        self.assertEqual(lastmsg, 'badxml/3/0//')

    def test_1000_extractMaths(self):
        model_path = get_path('beeler_reuter_1977-api-test.cellml')
        model = self.utility.loadModel(model_path, self.opener)
        maths = self.utility.extractMaths(model)
        self.assertEqual(len(maths), 12)
        # tuple of (cmetaId or name, list of equations)
        self.assertEqual(len(maths[1]), 2)
        # number of equations
        self.assertEqual(len(maths[1][1]), 1)
        self.assertEqual(maths[1][0], 'membrane')
        self.assert_(maths[1][1][0].startswith(
            '<math xmlns="http://www.w3.org/1998/Math/MathML"'))

    def test_2000_exportCeleds(self):
        model_path = get_path('beeler_reuter_1977.cellml')
        model = self.utility.loadModel(model_path, self.opener)
        code = self.utility.exportCeleds(model)
        # at least the language files we care about.
        self.assertTrue('Python' in code.keys())
        self.assertTrue('C' in code.keys())
        self.assertTrue('F77' in code.keys())
        self.assertTrue('MATLAB' in code.keys())
        self.assertTrue(code['Python'].startswith('# '))

    def test_3000_validateModel_clean(self):
        model_path = get_path('beeler_reuter_1977.cellml')
        model = self.utility.loadModel(model_path, self.opener)
        results = self.utility.validateModel(model)
        self.assertEqual(len(results), 0)

    def test_3000_validateModel_unclean(self):
        model_path = get_path('beeler_reuter_1977-api-test.cellml')
        model = self.utility.loadModel(model_path, self.opener)
        results = self.utility.validateModel(model)
        # Original model does not validate.
        self.assertNotEqual(len(results), 0)
        # Would test for the right strings to show up, but wording and
        # such may change...


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UtilityTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
