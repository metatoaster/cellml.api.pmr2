import urllib2
import urlparse

import zope.interface

from cellml_api import CellML_APISPEC

from cellml.api.pmr2.interfaces import ICellMLAPIUtility


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

    # XXX define these as part of schema
    approved_protocol = ['http', 'https']

    def __init__(self):
        self.cellml_bootstrap = CellML_APISPEC.CellMLBootstrap()
        self.model_loader = self.cellml_bootstrap.getmodelLoader()

    def _validateProtocol(self, location):
        return urlparse(location).scheme in self.approved_protocol

    def loadURL(self, location):
        if not self._validateProtocol:
            # XXX subclass this error may be better
            raise ValueError('protocol for the location is not approved')
        fd = urllib2.urlopen(location)
        result = fd.read()
        fd.close()
        return result

    def loadModel(self, model_url):
        """\
        Loads the CellML Model at the specified URL.

        This implementation does not use the built-in load model method
        in the model loader to avoid getting into non-reentrant issues
        that plagues that method.
        """

        def getImportGenerator(model):
            imports = model.getimports()
            importgen = makeGenerator(imports, key='Import')
            return importgen

        def appendQueue(base, model):
            # need to remember the source that this import was derived 
            # from, and use the xml:base of it if set.
            base_url = model.getxmlBase().getasText() or base
            subimport = list(getImportGenerator(model))
            if subimport:
                importq.append((base_url, subimport,))

        importq = []

        base = self.loadURL(model_url)
        model = self.model_loader.createFromText(base)
        appendQueue(model_url, model)

        while len(importq):
            # XXX base may be incorrect - check xml:base
            base, imports = importq.pop(0)
            for i in imports:
                relurl = i.getxlinkHref().getasText()
                nexturl = urlparse.urljoin(base, relurl)
                try:
                    base = self.loadURL(nexturl)
                except urllib2.URLError:
                    # XXX silently failing, should log somewhere
                    continue
                except ValueError:
                    # XXX subclass to better differentiate between this 
                    # and other ValueError
                    continue
                i.instantiateFromText(base)
                appendQueue(nexturl, i.getimportedModel())

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
        for component in makeGenerator(model.getallComponents(), 
                                       key='Component'):
            results.append((
                component.getcmetaId() or component.getname(),
                [self.cellml_bootstrap.serialiseNode(i) 
                    for i in makeGenerator(component.getmath())],
            ))
        return results

    def celeds(self):
        pass


def makeGenerator(obj, iterator='iterate', next='next', key=None):
    """\
    Takes the object and make a generator from a CellML API object.

    This is needed because the CellML API does not support standard
    iterators, and having them makes the API twice as easy to use.

    obj - object to attempt to get iterator from
    iterator - the iterator method
    next - the next method for the iterator
    key - short cut parameters; if set, this sets the iterator to be
          iterator${key}s and next to be next${key}
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

    if key is not None:
        iterator = 'iterate%ss' % key
        next = 'next%s' % key

    iobj = getcallable(obj, iterator)()
    nfunc = getcallable(iobj, next)
    return _generator(nfunc)
