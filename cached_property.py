# -*- coding: utf-8 -*-

__author__ = "Daniel Greenfeld"
__email__ = "pydanny@gmail.com"
__version__ = "1.5.1"
__license__ = "BSD"

import inspect
from time import time
import threading

try:
    import asyncio
except (ImportError, SyntaxError):
    asyncio = None


def _is_mangled(name):
    """Check whether a name will be mangled when accessed as an attribute."""
    return name.startswith("__") and not name.endswith("__")


def _resolve_name(klass, default=None):
    """Get the name of a function used to access it from an object."""
    name = default

    if _is_mangled(name) and klass:
        for base_cls in inspect.getmro(klass):
            resolved_name = "_{}{}".format(base_cls.__name__, name)
            if resolved_name in base_cls.__dict__:
                name = resolved_name
                break

    return name


class cached_property(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func, name=None):
        if not callable(func):
            func = None
            name = func
        self._name = name
        self._prepare_func(func)

    def __call__(self, func):
        self._prepare_func(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        name = self._name
        if not name:
            name = _resolve_name(cls, self.func.__name__)
            self._name = name

        if asyncio and asyncio.iscoroutinefunction(self.func):
            return self._wrap_in_coroutine(obj, name)

        value = obj.__dict__[name] = self.func(obj)
        return value

    def _wrap_in_coroutine(self, obj, name):
        @asyncio.coroutine
        def wrapper():
            future = asyncio.ensure_future(self.func(obj))
            obj.__dict__[name] = future
            return future

        return wrapper()

    def _prepare_func(self, func):
        self.func = func
        if func:
            self.__doc__ = func.__doc__
            self.__name__ = func.__name__
            self.__module__ = func.__module__


class threaded_cached_property(object):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, func, name=None):
        if not callable(func):
            func = None
            name = func
        self.__doc__ = getattr(func, "__doc__")
        self.func = func
        self._name = name
        self.lock = threading.RLock()
        self._prepare_func(func)

    def __call__(self, func):
        self._prepare_func(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        obj_dict = obj.__dict__
        name = self._name
        if not name:
            name = _resolve_name(cls, self.func.__name__)
            self._name = name
        with self.lock:
            try:
                # check if the value was computed before the lock was acquired
                return obj_dict[name]

            except KeyError:
                # if not, do the calculation and release the lock
                return obj_dict.setdefault(name, self.func(obj))

    def _prepare_func(self, func):
        self.func = func
        if func:
            self.__doc__ = func.__doc__
            self.__name__ = func.__name__
            self.__module__ = func.__module__


class cached_property_with_ttl(object):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Setting the ttl to a number expresses how long
    the property will last before being timed out.
    """

    def __init__(self, ttl=None, name=None):
        if callable(ttl):
            func = ttl
            ttl = None
        else:
            func = None
        self.ttl = ttl
        self._name = name
        self._prepare_func(func)

    def __call__(self, func):
        self._prepare_func(func)
        return self

    def __get__(self, obj, cls):
        if obj is None:
            return self

        now = time()
        obj_dict = obj.__dict__
        name = self._name
        if not name:
            name = _resolve_name(cls, self.__name__)
            self._name = name
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
        name = self._name
        if not name:
            cls = getattr(obj, "__class__", None)
            name = _resolve_name(cls, self.__name__)
            self._name = name
        obj.__dict__.pop(name, None)

    def __set__(self, obj, value):
        name = self._name
        if not name:
            cls = getattr(obj, "__class__", None)
            name = _resolve_name(cls, self.__name__)
            self._name = name
        obj.__dict__[name] = (value, time())

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
            return super(threaded_cached_property_with_ttl, self).__get__(obj, cls)


# Alias to make threaded_cached_property_with_ttl easier to use
threaded_cached_property_ttl = threaded_cached_property_with_ttl
timed_threaded_cached_property = threaded_cached_property_with_ttl
