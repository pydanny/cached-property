# -*- coding: utf-8 -*-

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '1.0.0'
__license__ = 'BSD'

from time import time
import threading


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property.

        Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
        """  # noqa

    def __init__(self, ttl=None):
        ttl_or_func = ttl
        self.ttl = None
        if callable(ttl_or_func):
            self.prepare_func(ttl_or_func)
        else:
            self.ttl = ttl_or_func

    def prepare_func(self, func, doc=None):
        '''Prepare to cache object method.'''
        self.func = func
        self.__doc__ = doc or func.__doc__
        self.__name__ = func.__name__
        self.__module__ = func.__module__

    def __call__(self, func, doc=None):
        self.prepare_func(func, doc)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time()
        try:
            value, last_update = obj._cache[self.__name__]
            if self.ttl and self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.func(obj)
            try:
                cache = obj._cache
            except AttributeError:
                cache = obj._cache = {}
            cache[self.__name__] = (value, now)

        return value

    def __delattr__(self, name):
        print(name)


class threaded_cached_property(cached_property):
    """ A cached_property version for use in environments where multiple
        threads might concurrently try to access the property.
        """
    def __init__(self, ttl=None):
        super(threaded_cached_property, self).__init__(ttl)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        with self.lock:
            # Double check if the value was computed before the lock was
            # acquired.
            prop_name = self.__name__
            if hasattr(obj, '_cache') and prop_name in obj._cache:
                return obj._cache[prop_name][0]

            # If not, do the calculation and release the lock.
            return super(threaded_cached_property, self).__get__(obj, cls)
