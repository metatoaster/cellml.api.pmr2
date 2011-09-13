import zope.interface


class ICellMLAPIUtility(zope.interface.Interface):

    def loadModel(model_url):
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
