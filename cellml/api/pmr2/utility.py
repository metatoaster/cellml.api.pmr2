import zope.interface

from cellml.api.pmr2.interfaces import ICellMLAPIUtility


class CellMLAPIUtility(object):
    """\
    from cellml.api.pmr2.interfaces import ICellMLAPIUtility
    import zope.component
    cu = zope.component.getUtility(ICellMLAPIUtility)
    """

    zope.interface.implements(ICellMLAPIUtility)

    def __init__(self):
        pass

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

        raise NotImplementedError

    def serialiseNode(self, node):
        """\
        see Interface.
        """

        raise NotImplementedError

    def extractMaths(self, model):
        """\
        see Interface.
        """

        results = []
        return results
