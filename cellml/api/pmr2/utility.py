from urllib2 import urlopen
from urlparse import urljoin

import zope.interface

from cellml_api import CellML_APISPEC

from cellml.api.pmr2.interfaces import ICellMLAPIUtility


class CellMLAPIUtility(object):
    """\
    from cellml.api.pmr2.interfaces import ICellMLAPIUtility
    import zope.component
    cu = zope.component.getUtility(ICellMLAPIUtility)
    """

    zope.interface.implements(ICellMLAPIUtility)

    def __init__(self):
        self.cellml_bootstrap = CellML_APISPEC.CellMLBootstrap()
        self.model_loader = self.cellml_bootstrap.getmodelLoader()

    def getGenerator(self, obj, iterator='iterate', next='next'):
        """\
        see Interface.
        """

        def _generator(func):
            while 1:
                next = func()
                if next is None:
                    raise StopIteration
                yield next

        def getcallable(obj, name):
            if not hasattr(obj, name):
                raise TypeError("'%s' object is not iterable with %s" % 
                                (obj.__class__.__name__, name))
            result = getattr(obj, name)
            if not callable(result):
                raise TypeError("'%s.%s' is not callable" % 
                                (obj.__class__.__name__, name))
            return result

        iobj = getcallable(obj, iterator)()
        nfunc = getcallable(iobj, next)
        return _generator(nfunc)

    def loadModel(self, url):
        """\
        see Interface.
        """

        # XXX as this is NOT reentrant safe, we need to do expand on
        # this using reentrant safe methods so we can GET ourselves.
        # XXX really should do our own model loading to pass in extra
        # authentication and/or cookies to propagate the requesting 
        # user's credentials to these internal requests.
        model = self.model_loader.loadFromURL(url)
        model.fullyInstantiateImports()
        return model

    def safeLoadModel(self, source_url):
        """\
        See Interface.
        """

        def loadurl(location):
            # XXX may need to sanitize URLs.
            # e.g. no loading from file://
            fd = urlopen(location)
            result = fd.read()
            fd.close()
            return result

        def getImportGenerator(model):
            imports = model.getimports()
            importgen = self.getGenerator(imports, 
                'iterateImports', 'nextImport')
            return importgen

        importq = []

        source = loadurl(source_url)
        model = self.model_loader.createFromText(source)
        importq.append((source_url, list(getImportGenerator(model))))

        while len(importq):
            # XXX base may be incorrect - check xml:base
            base, imports = importq.pop(0)
            for i in imports:
                relurl = i.getxlinkHref().getasText()
                nexturl = urljoin(base, relurl)
                source = loadurl(nexturl)
                i.instantiateFromText(source)
                im = i.getimportedModel()
                # check for further imports
                subimport = list(getImportGenerator(im))
                if subimport:
                    importq.append((nexturl, subimport))

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
        for element in self.getGenerator(model.getallComponents()):
            component = CellML_APISPEC.CellMLComponent(element)
            results.append((
                component.getcmetaId() or component.getname(),
                [self.cellml_bootstrap.serialiseNode(i) 
                    for i in self.getGenerator(component.getmath())],
            ))
        return results
