class singleton_property(object):
    """\
    Instantiate a single instance of this property for this instance.
    """

    def __init__(self, method):
        self.method = method

    def __get__(self, obj, objtype):
        """\
        Assign the outout of the met
        """

        name = '_%s' % self.method.__name__
        result = getattr(obj, name, None)
        if not result:
            result = self.method(obj)
            setattr(obj, name, result)
        return result
