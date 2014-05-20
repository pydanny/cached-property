# -*- coding: utf-8 -*-

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '0.1.4'
__license__ = 'BSD'

import time
import threading


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        """

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class threaded_cached_property(cached_property):
    """ A cached_property version for use in environments where multiple
        threads might concurrently try to access the property.
        """
    def __init__(self, func):
        super(threaded_cached_property, self).__init__(func)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        with self.lock:
            # Double check if the value was computed before the lock was
            # acquired.
            prop_name = self.func.__name__
            if prop_name in obj.__dict__:
                return obj.__dict__[prop_name]

            # If not, do the calculation and release the lock.
            return super(threaded_cached_property, self).__get__(obj, cls)