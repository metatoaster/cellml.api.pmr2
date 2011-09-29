import zope.interface
import zope.schema


class UnapprovedProtocolError(ValueError):
    """\
    protocol is unapproved.
    """


class ICellMLAPIUtility(zope.interface.Interface):

    celeds_exporter = zope.schema.Dict(
        title=u'Available CeLEDS exporter',
        description=u'Dictionary of the instantiated CeLEDS exporter '
                     'available for usage',
        key_type=zope.schema.ASCIILine(title=u'Protocol type'),
        #value_type=zope.schema.Object(),
        required=False,
    )

    def availableCeledsExporter():
        """\
        The list of available CeLEDS exporter.
        """

    def loadModel(model_url, opener=None):
        """\
        Loads a model from the given url.

        model_url - URL of the model
        opener - callable function that can load the desired url.
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

    def exportCeleds(model, language=None):
        """\
        Run the model through one or all of the available CeLEDS 
        Exporter.
        """


class IURLOpener(zope.interface.Interface):
    """\
    Interface for the URL Opener

    Contains methods that will control a list of permissible URL schemes
    and other special methods.

    Callable must call and return loadURL.
    """

    approved_protocol = zope.schema.List(
        title=u'Approved Protocols',
        description=u'The list of approved protocols to acquire models from',
        value_type=zope.schema.ASCIILine(title=u'Protocol type'),
        unique=True,
        required=False,
    )

    def validateProtocol(location):
        """\
        Validate the location to check if URL is allowed to be opened.
        """

    def loadURL(location, headers=None):
        """\
        The method that opens the URL and return the contents as a 
        string.

        location - the location to open
        headers - a list of key/value pairs of the headers to add.
        """
