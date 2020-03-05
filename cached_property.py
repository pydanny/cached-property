# -*- coding: utf-8 -*-

__author__ = "Daniel Greenfeld"
__email__ = "pydanny@gmail.com"
__version__ = "1.5.1"
__license__ = "BSD"

from functools import wraps
from time import time
import threading

try:
    import asyncio
except (ImportError, SyntaxError):
    asyncio = None


class CachedProperty(object):
    """Parent class for cached properties."""

    # As of now, it is only used for ``isinstance`` tests. Cf. ``cached_properties_names``.
    pass


class cached_property(CachedProperty):
    """
    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """  # noqa

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        if asyncio and asyncio.iscoroutinefunction(self.func):
            return self._wrap_in_coroutine(obj)

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value

    def _wrap_in_coroutine(self, obj):
        @wraps(obj)
        @asyncio.coroutine
        def wrapper():
            future = asyncio.ensure_future(self.func(obj))
            obj.__dict__[self.func.__name__] = future
            return future

        return wrapper()


class threaded_cached_property(CachedProperty):
    """
    A cached_property version for use in environments where multiple threads
    might concurrently try to access the property.
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func
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


class cached_property_with_ttl(CachedProperty):
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
            return super(threaded_cached_property_with_ttl, self).__get__(obj, cls)


# Alias to make threaded_cached_property_with_ttl easier to use
threaded_cached_property_ttl = threaded_cached_property_with_ttl
timed_threaded_cached_property = threaded_cached_property_with_ttl


def all_members(cls):
    """All members of a class.

    Credit: Jürgen Hermann, Alex Martelli. From
    https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s03.html.


    Parameters
    ----------
    cls : class

    Returns
    -------
    dict
        Similar to ``cls.__dict__``, but include also the inherited members.

    Examples
    --------
    >>> class Parent(object):
    ...     attribute_parent = 42
    >>> class Child(Parent):
    ...     attribute_child = 51
    >>> 'attribute_child' in all_members(Child).keys()
    True
    >>> 'attribute_parent' in all_members(Child).keys()
    True
    """
    try:
        # Try getting all relevant classes in method-resolution order
        mro = list(cls.__mro__)
    except AttributeError:
        # If a class has no _ _mro_ _, then it's a classic class
        def getmro(a_class, recurse):
            an_mro = [a_class]
            for base in a_class.__bases__:
                an_mro.extend(recurse(base, recurse))
            return an_mro

        mro = getmro(cls, getmro)
    mro.reverse()
    members = {}
    for someClass in mro:
        members.update(vars(someClass))
    return members


def cached_properties(o):
    """Cached properties (whether already computed or not).

    Parameters
    ----------
    o : object

    Yields
    ------
    str
        Name of each cached property.

    Examples
    --------
    >>> class MyClass(object):
    ...     @cached_property
    ...     def my_cached_property(self):
    ...         print('Computing my_cached_property...')
    ...         return 2
    ...     @cached_property
    ...     def my_second_cached_property(self):
    ...         print('Computing my_second_cached_property...')
    ...         return 3
    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    Computing my_cached_property...
    2
    >>> for name in cached_properties(my_object):
    ...     print(name)
    my_cached_property
    my_second_cached_property
    """
    return (
        k for k, v in all_members(o.__class__).items() if isinstance(v, CachedProperty)
    )


def cached_properties_computed(o):
    """Cached properties that are already computed.

    Parameters
    ----------
    o : object

    Yields
    ------
    str
        Name of each cached property that is already computed.

    Examples
    --------
    >>> class MyClass(object):
    ...     @cached_property
    ...     def my_cached_property(self):
    ...         print('Computing my_cached_property...')
    ...         return 2
    ...     @cached_property
    ...     def my_second_cached_property(self):
    ...         print('Computing my_second_cached_property...')
    ...         return 3
    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    Computing my_cached_property...
    2
    >>> for name in cached_properties_computed(my_object):
    ...     print(name)
    my_cached_property
    """
    return (k for k in cached_properties(o) if k in o.__dict__.keys())


def delete_cache(o):
    """Delete the cache.

    Parameters
    ----------
    o : object

    Examples
    --------
    >>> class MyClass(object):
    ...     @cached_property
    ...     def my_cached_property(self):
    ...         print('Computing my_cached_property...')
    ...         return 2
    ...     @cached_property
    ...     def my_second_cached_property(self):
    ...         print('Computing my_second_cached_property...')
    ...         return 3
    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    Computing my_cached_property...
    2
    >>> delete_cache(my_object)
    >>> my_object.my_cached_property
    Computing my_cached_property...
    2
    """
    for cached_property_name in cached_properties(o):
        try:
            del o.__dict__[cached_property_name]
        except KeyError:
            pass


class property_deleting_cache:
    """A property that deletes the cache when set or deleted.

    Parameters
    ----------
    func : function
        Each time we get the property, this function is run for the sake of
        its side effects (but its return value is ignored); then the value of
        the property is accessed.

    Examples
    --------
    >>> class MyClass(object):
    ...     def __init__(self, my_parameter):
    ...         self.my_parameter = my_parameter
    ...     @property_deleting_cache
    ...     def my_parameter(self):
    ...         "A parameter that deletes the cache when set or deleted."
    ...         print('Accessing my_parameter...')
    ...     @cached_property
    ...     def my_cached_property(self):
    ...         print('Computing my_cached_property...')
    ...         return self.my_parameter + 1
    >>> my_object = MyClass(my_parameter=41)
    >>> my_object.my_cached_property
    Computing my_cached_property...
    Accessing my_parameter...
    42
    >>> my_object.my_parameter = 50
    >>> my_object.my_cached_property
    Computing my_cached_property...
    Accessing my_parameter...
    51
    >>> MyClass.my_parameter.__doc__
    'A parameter that deletes the cache when set or deleted.'
    """

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        self.func(obj)
        return self.value

    def __set__(self, obj, value):
        delete_cache(obj)
        self.value = value

    def __delete__(self, obj):
        delete_cache(obj)
        del self.value


class property_deleting_cache_2:
    """Define a property that deletes the cache when set or deleted.

    Parameters
    ----------
    doc : str
        The documentation of the property

    Examples
    --------
    >>> class MyClass(object):
    ...     def __init__(self, my_parameter):
    ...         self.my_parameter = my_parameter
    ...     my_parameter = property_deleting_cache_2(
    ...         doc="A parameter that deletes the cache when set or deleted.")
    ...     @cached_property
    ...     def my_cached_property(self):
    ...         print('Computing my_cached_property...')
    ...         return self.my_parameter + 1
    >>> my_object = MyClass(my_parameter=41)
    >>> my_object.my_cached_property
    Computing my_cached_property...
    42
    >>> my_object.my_parameter = 50
    >>> my_object.my_cached_property
    Computing my_cached_property...
    51
    >>> MyClass.my_parameter.__doc__
    'A parameter that deletes the cache when set or deleted.'
    """

    def __init__(self, doc):
        self.__doc__ = doc

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return self.value

    def __set__(self, obj, value):
        delete_cache(obj)
        self.value = value

    def __delete__(self, obj):
        delete_cache(obj)
        del self.value
