# -*- coding: utf-8 -*-

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '0.1.2'
__license__ = 'BSD'


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property. """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value
