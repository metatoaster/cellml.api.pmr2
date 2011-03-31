import zope.interface


class ICellMLAPIUtility(zope.interface.Interface):

    def getGenerator(obj):
        """\
        Converts the CellML API object into a pythonic generator.
        """

    def loadModel(url):
        """\
        Loads a model from the given url.
        """

    def serialiseNode(node):
        """\
        Serialise a node.
        """

    def extractMaths(model):
        """\
        Extract and serialize the maths into a list of tuples for ease
        of presentation in the MathML viewer.
        """
