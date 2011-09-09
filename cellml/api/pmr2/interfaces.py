import zope.interface


class ICellMLAPIUtility(zope.interface.Interface):

    def getGenerator(obj):
        """\
        Converts the CellML API object into a pythonic generator.
        """

    def loadModel(url):
        """\
        Loads a model from the given url.

        Pending implementation of the API itself, this method may block
        other threads as this is not reentrant safe.
        """

    def safeLoadModel(url):
        """\
        Loads a model from the given url, safely.

        Whatever this means, but this method will use multiprocessing to
        spawn a new thread that will load the model, thus even if it's
        not reentrant safe it should not block other threads of the
        current process.
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
