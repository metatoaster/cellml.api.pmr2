from cStringIO import StringIO
from lxml import etree
import zope.interface

from cellml.api.pmr2.interfaces import ICellMLAPIUtility

from cellml.api.simple import mathml


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

        # XXX since we don't actually have the bindings ready, this only
        # pretend to do something.
        self.url = url

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
        maths = mathml(self.url)
        namespaces = {'mml': 'http://www.w3.org/1998/Math/MathML'}
        t = etree.parse(StringIO(maths))
        results = [
            (
                # component name or id
                comps.xpath('h3')[0].text,
                [
                    # list of mathml nodes
                    etree.tostring(n) for n in comps.xpath(
                        'div/mml:math',
                        namespaces=namespaces
                    )
                ]
            )
            for comps in t.xpath('/div/div')
        ]
        return results

