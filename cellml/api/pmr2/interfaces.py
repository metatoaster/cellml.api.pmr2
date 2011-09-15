import zope.interface
import zope.schema


class ICellMLAPIUtility(zope.interface.Interface):

    approved_protocol = zope.schema.List(
        title=u'Approved Protocols',
        description=u'The list of approved protocols to acquire models from',
        value_type=zope.schema.ASCIILine(title=u'Protocol type'),
        unique=True,
        required=False,
    )

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

    def loadURL(location):
        """\
        Loads location, return contents as a string.

        Location must be located at an approved protocol.
        """

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

    def exportCeleds(model, language=None):
        """\
        Run the model through one or all of the available CeLEDS 
        Exporter.
        """
