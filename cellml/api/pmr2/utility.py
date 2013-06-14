from os import listdir

from os.path import join
from os.path import dirname
from os.path import splitext

from cStringIO import StringIO

from lxml import etree
import urllib2
import urlparse

import zope.interface
from zope.schema.fieldproperty import FieldProperty

import cgrspy.bootstrap

from cellml.api.pmr2.interfaces import ICellMLAPIUtility
from cellml.api.pmr2.interfaces import IURLOpener
from cellml.api.pmr2.interfaces import UnapprovedProtocolError

from cellml.api.pmr2.property import singleton_property
from cellml.api.pmr2.urlopener import DefaultURLOpener

_root = dirname(__file__)
resource_file = lambda *p: join(_root, 'resource', *p)


class CellMLAPIUtility(object):
    """\
    A more pythonic wrapper for the CellML API Python bindings.

    This class provides a few useful utilities that simplifies the 
    interaction with the CellML API from within Python, such as a better
    model loader, providing a wrapper for getting a generator to the
    lists, and in this case provdes some integration with PMR2.

    If this class is registered within ZCA, the CellML API can be
    acquired with::
    
        from cellml.api.pmr2.interfaces import ICellMLAPIUtility
        import zope.component
        api_util = zope.component.getUtility(ICellMLAPIUtility)
    """

    zope.interface.implements(ICellMLAPIUtility)

    celeds_exporter = FieldProperty(ICellMLAPIUtility['celeds_exporter'])

    def __init__(self):
        # set non-primative defaults
        self.celeds_exporter = {}

        # other initializations
        self._initiateCeLEDS()

    @singleton_property
    def url_opener(self):
        return DefaultURLOpener()

    @singleton_property
    def celeds_bootstrap(self):
        cgrspy.bootstrap.loadGenericModule('cgrs_celeds')
        celeds_bootstrap = cgrspy.bootstrap.fetch(
            'CreateCeLEDSBootstrap')
        return celeds_bootstrap

    @singleton_property
    def celedsexporter_bootstrap(self):
        cgrspy.bootstrap.loadGenericModule('cgrs_celedsexporter')
        celedsexporter_bootstrap = cgrspy.bootstrap.fetch(
            'CreateCeLEDSExporterBootstrap')
        return celedsexporter_bootstrap

    @singleton_property
    def cellml_bootstrap(self):
        cgrspy.bootstrap.loadGenericModule('cgrs_cellml')
        cellml_bootstrap = cgrspy.bootstrap.fetch('CreateCellMLBootstrap')
        return cellml_bootstrap

    @singleton_property
    def model_loader(self):
        return self.cellml_bootstrap.modelLoader

    @singleton_property
    def vacs_service(self):
        cgrspy.bootstrap.loadGenericModule('cgrs_vacss')
        vacs_service = cgrspy.bootstrap.fetch('CreateVACSService')
        return vacs_service

    def _initiateCeLEDS(self):
        """\
        Instantiate all CeLEDS definition files within the resource
        directory as exporters.
        """

        for filename in listdir(resource_file('celeds')):
            fd = open(resource_file('celeds', filename))
            raw = fd.read()
            fd.close()

            key, ext = splitext(filename)
            exporter = self.celedsexporter_bootstrap.createExporterFromText(raw)

            self.celeds_exporter[key] = exporter

    def availableCeledsExporter(self):
        """
        """

        return self.celeds_exporter.key()

    def loadModel(self, model_url, loader=None):
        """\
        Loads the CellML Model at the specified URL.

        This implementation does not use the built-in load model method
        in the model loader to avoid getting into non-reentrant issues
        that plagues that method.

        The optional loader parameter allows the caller to replace with
        a specialized version (subclassed from BaseURLOpener) that will
        be used to load the model_url.
        """

        def appendQueue(base, model):
            # need to remember the source that this import was derived 
            # from; use the xml:base of the model if available.
            base_url = model.xmlBase.asText or base
            subimports = model.imports
            importq.append((base_url, subimports,))

        if loader is None:
            loader = self.url_opener
        assert IURLOpener.providedBy(loader)

        importq = []
        model_string = loader(model_url)
        # workaround for lack of encoding detection regardless of input.
        try:
            encoding = etree.load(StringIO(model_string)).docinfo.encoding
        except:
            encoding = 'ISO-8859-1'
        model = self.model_loader.createFromText(model_string.decode(encoding))
        appendQueue(model_url, model)

        while len(importq):
            base, imports = importq.pop(0)
            for i in imports:
                relurl = i.xlinkHref.asText
                nexturl = urlparse.urljoin(base, relurl)
                try:
                    source = loader(nexturl)
                except urllib2.URLError:
                    # XXX silently failing, should log somewhere
                    continue
                except UnapprovedProtocolError:
                    continue
                i.instantiateFromText(source)
                appendQueue(nexturl, i.importedModel)

        return model

    def serialiseNode(self, node):
        """\
        see Interface.
        """

        return self.cellml_bootstrap.serialiseNode(node)

    def extractMaths(self, model):
        """\
        see Interface.
        """

        results = []
        for component in model.allComponents:
            results.append((
                component.cmetaId or component.name,
                [self.serialiseNode(i) for i in component.math],
            ))
        return results

    def exportCeleds(self, model, language=None):
        """\
        Export model to the target language(s) through CeLEDS.

        This uses the CellML Code Generation Service through the 
        CellML Language Export Definition Service exporter.

        model - the model object.
        language - a list of languages to generate output for.
                   if language is not available it will not be
                   used.
        """

        result = {}

        for key, exporter in self.celeds_exporter.iteritems():
            if language and k not in language:
                continue
            code = exporter.generateCode(model)
            result[key] = code

        return result

    def validateModel(self, model):
        """\
        Validate model.
        """

        def iterateResultSet(rs):
            for i in xrange(rs.nValidityErrors):
                yield rs.getValidityError(i)

        result = []  # list of error messages.
        vrset = self.vacs_service.validateModel(model)
        for error in iterateResultSet(vrset): #listResultSet(vrset):
            # have to manually cast things to get the type that will
            # be able to compute the location... why can't these be
            # computed properties...
            errstr = error.description
            errtype = error.isWarningOnly and 'Warning' or 'Error'
            errnode = error.errorNode
            # since offset appears to be specific to row and we don't
            # calculate that, assume 1 to offset the xml header.
            errrow, errcol = self.vacs_service.getPositionInXML(errnode, 1)

            result.append('Line %d, Col %d: %s: %s' % 
                (errrow, errcol, errtype, errstr))

        return result
