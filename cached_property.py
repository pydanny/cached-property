# -*- coding: utf-8 -*-

__author__ = "Daniel Greenfeld"
__email__ = "pydanny@gmail.com"
__version__ = "1.5.1"
__license__ = "BSD"

import functools
import threading
from time import time

try:
    import asyncio
except (ImportError, SyntaxError):
    asyncio = None


class cached_property(property):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.value = self._sentinel = object()
        self.func = func
        functools.wraps(func, self)

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if asyncio and asyncio.iscoroutinefunction(self.func):
            return self._wrap_in_coroutine(obj)
        if self.value is self._sentinel:
            self.value = self.func(obj)
        return self.value

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __set__(self, obj, value):
        self.value = value

    def __delete__(self, obj):
        self.value = self._sentinel

    def _wrap_in_coroutine(self, obj):
        @asyncio.coroutine
        def wrapper():
            if self.value is self._sentinel:
                self.value = asyncio.ensure_future(self.func(obj))
            return self.value

        return wrapper()


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
        with self.lock:
            return super(threaded_cached_property, self).__get__(obj, cls)

    def __set__(self, obj, value):
        with self.lock:
            super(threaded_cached_property, self).__set__(obj, value)

    def __delete__(self, obj):
        with self.lock:
            super(threaded_cached_property, self).__delete__(obj)


class cached_property_with_ttl(cached_property):
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
        super(cached_property_with_ttl, self).__init__(func)

    def __call__(self, func):
        super(cached_property_with_ttl, self).__init__(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time()
        if self.value is not self._sentinel:
            value, last_updated = self.value
            if not self.ttl or self.ttl > now - last_updated:
                return value

        self.value = value, _ = (self.func(obj), now)
        return value

    def __set__(self, obj, value):
        super(cached_property_with_ttl, self).__set__(obj, (value, time()))


# Aliases to make cached_property_with_ttl easier to use
cached_property_ttl = cached_property_with_ttl
timed_cached_property = cached_property_with_ttl


class threaded_cached_property_with_ttl(
    cached_property_with_ttl, threaded_cached_property
):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, ttl=None):
        super(threaded_cached_property_with_ttl, self).__init__(ttl)
        self.lock = threading.RLock()

    def __get__(self, obj, cls):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__get__(obj, cls)

    def __set__(self, obj, value):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__set__(obj, value)

    def __delete__(self, obj):
        with self.lock:
            return super(threaded_cached_property_with_ttl, self).__delete__(obj)


# Alias to make threaded_cached_property_with_ttl easier to use
threaded_cached_property_ttl = threaded_cached_property_with_ttl
timed_threaded_cached_property = threaded_cached_property_with_ttl
