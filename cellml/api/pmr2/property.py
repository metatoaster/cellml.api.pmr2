# perhaps we could inherit from property instead of object?
# Obvious none of this is considered thread-safe.

class base_property(object):

    def __init__(self, method):
        self.method = method

    @property
    def name(self):
        return '_%s' % self.method.__name__


class instance_property(base_property):
    """\
    Property decorator that automate caching of the first result.

    This decorator checks whether there was a result that was cached by
    the parent object, if not, calls the property method, cache it then
    return the cached result.
    """

    def __get__(self, obj, objtype):
        """\
        Assign the outout of the met
        """

        name = self.name
        result = getattr(obj, name, None)
        if result is None:
            result = self.method(obj)
            setattr(obj, name, result)
        return result

    def __delete__(self, obj):
        """\
        Delete the property.
        """
        
        name = self.name
        result = getattr(obj, name, None)
        if result is None:
            return
        delattr(obj, name)


class singleton_property(base_property):
    """\
    Property decorator that automate caching of the first result in this
    decorator instance.

    Basically this instantiate a single instance of the property 
    referenced by this class into this decorator instance, thus all
    subsequent attempts will return this instance, functionally 
    equivalent to a singleton that is the same across all instances of
    the object.
    """

    def __get__(self, obj, objtype):
        """\
        Assign the outout of the met
        """

        name = self.name
        result = getattr(self, name, None)
        if result is None:
            result = self.method(obj)
            setattr(self, name, result)
        return result

    def __delete__(self, obj):
        """\
        Delete the property.
        """
        
        name = self.name
        result = getattr(self, name, None)
        if result is None:
            return
        delattr(self, name)
