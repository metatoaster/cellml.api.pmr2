import zope.interface

from cellmlapi import CellML_APISPEC

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

    def getGenerator(self, obj):
        """\
        see Interface.
        """

        def _generator(iterate):
            while 1:
                next = iterate.next()
                if next is None:
                    raise StopIteration
                yield next

        if not (hasattr(obj, 'iterate') and callable(obj.iterate)):
            raise TypeError("'%s' object is not iterable" % 
                            obj.__class__.__name__)

        return _generator(obj.iterate())

    def loadModel(self, url):
        """\
        see Interface.
        """

        # XXX as this is NOT reentrant safe, we need to do expand on
        # this using reentrant safe methods so we can GET ourselves.
        return self.model_loader.loadFromURL(url)

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
