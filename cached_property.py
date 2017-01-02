# -*- coding: utf-8 -*-

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '1.3.0'
__license__ = 'BSD'

from time import time
import threading


class DummyLock(object):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass


class CachedProperty(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Setting the ttl to a number expresses how long
    the property will last before being timed out.
    """

    def __init__(self, ttl=None, threaded=False):
        if callable(ttl):
            func = ttl
            ttl = None
        else:
            func = None
        self.ttl = ttl
        self._prepare_func(func)
        self.cached_time = None
        self.cached = None
        if threaded:
            self.lock = threading.RLock()
        else:
            self.lock = DummyLock()

    def _prepare_func(self, func):
        if func:
            self.__doc__ = func.__doc__
            self.__name__ = func.__name__
            self.__module__ = func.__module__
        self.func = func

    def __call__(self, func):
        self._prepare_func(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        obj_dict = obj.__dict__
        name = self.__name__
        with self.lock:
            now = time()
            ttl_expired = self.cached_time is None or self.ttl and self.ttl < now - self.cached_time
            if not ttl_expired:
                return self.cached
            self.cached = self.func(obj)
            self.cached_time = now
            return self.cached

    def __delete__(self, obj):
        self.cached = None
        self.cached_time = None

    def __set__(self, obj, value):
        self.cached = value
        self.cached_time = time()

cached_property = CachedProperty

class cached_property_with_ttl(CachedProperty):
    pass

class threaded_cached_property(CachedProperty):
    def __init__(self, func_or_ttl):
        super(threaded_cached_property, self).__init__(func_or_ttl, threaded=True)


# Aliases to make cached_property_with_ttl easier to use
cached_property_ttl = cached_property_with_ttl
timed_cached_property = cached_property_with_ttl


class threaded_cached_property_with_ttl(cached_property_with_ttl):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, ttl=None):
        super(threaded_cached_property_with_ttl, self).__init__(ttl)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__get__(obj,
                                                                          cls)

# Alias to make threaded_cached_property_with_ttl easier to use
threaded_cached_property_ttl = threaded_cached_property_with_ttl
timed_threaded_cached_property = threaded_cached_property_with_ttl
