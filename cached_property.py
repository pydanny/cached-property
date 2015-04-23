# -*- coding: utf-8 -*-

__author__ = 'Daniel Greenfeld'
__email__ = 'pydanny@gmail.com'
__version__ = '1.0.0'
__license__ = 'BSD'

from time import time
import threading


def cachedproperty(func=None, ttl=None, threadsafe=False):
    """
    A property that is computed at most once per instance and then replaces
    itself with an ordinary attribute. Deleting the attribute resets the
    property. Usage:

        class Stuff(object):

            # A cached property can be defined as a decorator
            @cachedproperty
            def foo(self):
                ...

            # ... or a decorator factory:
            @cachedproperty(ttl=1)
            def bar(self):
                ...

            # or explicitly by a function call:

            def baz(self):
                ...

            cached_baz = cachedproperty(baz, threadsafe=True)

    :param ttl: Max time (in seconds) the property can stay cached. By default
        cached properties don't expire unless explicitly deleted.
    :param threadsafe: Pass True if the property might be accessed concurrently
        by multiple threads.
    """
    if ttl is None:
        if not threadsafe:
            decorator = cached_property
        else:
            decorator = threaded_cached_property
    else:
        if not threadsafe:
            decorator = cached_property_with_ttl(ttl)
        else:
            decorator = threaded_cached_property_with_ttl(ttl)

    return decorator(func) if func is not None else decorator


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class threaded_cached_property(cached_property):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, func):
        super(threaded_cached_property, self).__init__(func)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        if obj is None:
            return self

        obj_dict = obj.__dict__
        name = self.func.__name__
        with self.lock:
            try:
                # check if the value was computed before the lock was acquired
                return obj_dict[name]
            except KeyError:
                # if not, do the calculation and release the lock
                return obj_dict.setdefault(name, self.func(obj))


class cached_property_with_ttl(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Setting the ttl to a number expresses how long
    the property will last before being timed out.
    """

    def __init__(self, ttl=None):
        if callable(ttl):
            func = ttl
            ttl = None
        else:
            func = None
        self.ttl = ttl
        self._prepare_func(func)

    def __call__(self, func):
        self._prepare_func(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time()
        obj_dict = obj.__dict__
        name = self.__name__
        try:
            value, last_updated = obj_dict[name]
        except KeyError:
            pass
        else:
            ttl_expired = self.ttl and self.ttl < now - last_updated
            if not ttl_expired:
                return value

        value = self.func(obj)
        obj_dict[name] = (value, now)
        return value

    def __delete__(self, obj):
        obj.__dict__.pop(self.__name__, None)

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = (value, time())

    def _prepare_func(self, func):
        self.func = func
        if func:
            self.__doc__ = func.__doc__
            self.__name__ = func.__name__
            self.__module__ = func.__module__

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
