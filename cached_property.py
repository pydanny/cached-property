# -*- coding: utf-8 -*-

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '0.1.5'
__license__ = 'BSD'

import threading
import time


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        """

    def __init__(self, ttl=None):
        self.ttl = ttl
        
    def __call__(func, doc=None):
        self.__doc__ = doc or getattr(func, '__doc__')
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        
        self.func = func
        
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if not self.ttl:
            value = obj.__dict__[self.func.__name__] = self.func(obj)
            return value
        else:
            now = time.time()
            key = '_cached_' + self.func.__name__
            try:
                value, last_update = obj.__dict__[key]
                if self.ttl > 0 and now - last_update > self.ttl:
                    raise AttributeError
            except (KeyError, AttributeError):
                value = self.func(obj)
                obj.__dict__[key] = (value, now)
            
            return value


class threaded_cached_property(cached_property):
    """ A cached_property version for use in environments where multiple
        threads might concurrently try to access the property.
        """
    def __init__(self, ttl=None):
        super(threaded_cached_property, self).__init__(ttl=None)
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
