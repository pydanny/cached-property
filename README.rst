===============================
cached-property
===============================

.. image:: https://img.shields.io/pypi/v/cached-property.svg
    :target: https://pypi.python.org/pypi/cached-property

.. image:: https://img.shields.io/travis/pydanny/cached-property/master.svg
    :target: https://travis-ci.org/pydanny/cached-property
        
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black
    :alt: Code style: black        


A decorator for caching properties in classes.

Why?
-----

* Makes caching of time or computational expensive properties quick and easy.
* Because I got tired of copy/pasting this code from non-web project to non-web project.
* I needed something really simple that worked in Python 2 and 3.

How to use it
--------------

Let's define a class with an expensive property. Imagine that the "print"
instruction in this example represents a long computation:

.. code-block:: python

    class MyClass(object):

        @property
        def my_property(self):
            # In reality, this might represent a database call or time
            # intensive task like calling a third-party API.
            print('Computing my_property...')
            return 42

Now run it:

.. code-block:: python

    >>> my_object = MyClass()
    >>> my_object.my_property
    Computing my_property...
    42
    >>> my_object.my_property
    Computing my_property...
    42

Let's convert this property into a ``cached_property``:

.. code-block:: python

    from cached_property import cached_property

    class MyClass(object):

        @cached_property
        def my_cached_property(self):
            print('Computing my_cached_property...')
            return 42

Now when we run it the computation is performed only once:

.. code-block:: python

    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    Computing my_property...
    42
    >>> my_object.my_cached_property
    42
    >>> my_object.my_cached_property
    42

Why doesn't the value of ``my_object.my_cached_property`` change? Because it's
a **cached property**!

Inspecting the cache
--------------------

Sometimes you may want to list all the cached properties of an object. In
order to demonstrate this, let us define a class with several cached
properties:

.. code-block:: python

    from cached_property import cached_property

    class MyClass(object):

        @cached_property
        def my_cached_property(self):
            print('Computing my_cached_property...')
            return 42

        @cached_property
        def my_second_cached_property(self):
            print('Computing my_second_cached_property...')
            return 51

To list all the cached properties of an object, use the function
``cached_properties``:

.. code-block:: python

    >>> from cached_property import cached_properties
    >>> my_object = MyClass()
    >>> for property_name in cached_properties(my_object):
    ...     print(property_name)
    my_cached_property
    my_second_cached_property

To test which properties are already cached, use ``is_cached``:

.. code-block:: python

    >>> from cached_property import is_cached
    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    Computing my_property...
    42
    >>> is_cached(my_object, 'my_cached_property')
    True
    >>> is_cached(my_object, 'my_second_cached_property')
    False

Invalidating the Cache
----------------------

Results of cached functions can be invalidated by outside forces. To
demonstrate this, let's define first an object as we already did:

    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    Computing my_cached_property...
    42
    >>> my_object.my_second_cached_property
    Computing my_second_cached_property...
    51

To delete the cache for one property in particular, use ``un_cache``:

.. code-block:: python

    >>> from cached_property import un_cache
    >>> un_cache(my_object, 'my_cached_property')
    >>> my_object.my_cached_property
    Computing my_cached_property...
    42
    >>> my_object.my_second_cached_property
    51

To delete the cache of the whole object, use ``delete_cache``:

.. code-block:: python

    >>> from cached_property import delete_cache
    >>> delete_cache(my_object)
    >>> my_object.my_cached_property
    Computing my_cached_property...
    42
    >>> my_object.my_second_cached_property
    Computing my_second_cached_property...
    51

Property deleting the cache
---------------------------

Sometimes, you want to define a property that automatically deletes the cache
of the object when the property is set or deleted. You can use
``property_deleting_cache``:

.. code-block:: python

    from cached_property import cached_property, property_deleting_cache

    class MyClass(object):

        def __init__(self, my_parameter):
            self.my_parameter = my_parameter

        @property_deleting_cache
        def my_parameter(self):
            print('Accessing my_parameter...')

        @cached_property
        def my_cached_property(self):
            print('Computing my_cached_property...')
            return self.my_parameter + 1

Then use it:

.. code-block:: python

    >>> my_object = MyClass(my_parameter=41)
    >>> my_object.my_cached_property
    Computing my_cached_property...
    Accessing my_parameter...
    42
    >>> my_object.my_cached_property
    42
    >>> my_object.my_parameter = 50
    >>> my_object.my_cached_property
    Computing my_cached_property...
    Accessing my_parameter...
    51
    >>> my_object.my_cached_property
    51

Working with Threads
---------------------

What if a whole bunch of people want to access ``my_cached_property``
all at once? This means using threads, which unfortunately causes problems
with the standard ``cached_property``. In this case, switch to using the
``threaded_cached_property``:

.. code-block:: python

    from cached_property import threaded_cached_property

    class MyClass(object):

        @threaded_cached_property
        def my_cached_property(self):
            print('Computing my_cached_property...')
            return 42

Now use it:

.. code-block:: python

    >>> from threading import Thread
    >>> my_object = MyClass()
    >>> threads = []
    >>> for x in range(10):
    ...     thread = Thread(target=lambda: my_object.my_cached_property)
    ...     thread.start()
    ...     threads.append(thread)

    >>> for thread in threads:
    ...     thread.join()
    Computing my_cached_property...

Please note that ``my_cached_property`` was computed only once, as usual.

Working with async/await (Python 3.5+)
--------------------------------------

The cached property can be async, in which case you have to use await
as usual to get the value. Because of the caching, the value is only
computed once and then cached:

.. code-block:: python

    from cached_property import cached_property

    class MyClass(object):

        @cached_property
        async def my_cached_property(self):
            print('Computing my_cached_property...')
            return 42

Now use it:

.. code-block:: python

    >>> async def print_my_cached_property():
    ...     my_object = MyClass()
    ...     print(await my_object.my_cached_property)
    ...     print(await my_object.my_cached_property)
    ...     print(await my_object.my_cached_property)
    >>> import asyncio
    >>> asyncio.get_event_loop().run_until_complete(print_my_cached_property())
    Computing my_cached_property...
    42
    42
    42

Note that this does not work with threading either, most asyncio
objects are not thread-safe. And if you run separate event loops in
each thread, the cached version will most likely have the wrong event
loop. To summarize, either use cooperative multitasking (event loop)
or threading, but not both at the same time.

Timing out the cache
--------------------

Sometimes you want the price of things to reset after a time. Use the ``ttl``
versions of ``cached_property`` and ``threaded_cached_property``.

.. code-block:: python

    import random
    from cached_property import cached_property_with_ttl

    class MyClass(object):

        @cached_property_with_ttl(ttl=2) # cache invalidates after 2 seconds
        def my_cached_property(self):
            print('Computing my_cached_property...')
            return random.randint(1, 100)

Now use it:

.. code-block:: python

    >>> my_object = MyClass()
    >>> my_object.my_cached_property
    42
    >>> my_object.my_cached_property
    42
    >>> from time import sleep
    >>> sleep(3)  # Sleeps long enough to expire the cache
    >>> my_object.my_cached_property
    51

**Note:** The ``ttl`` tools do not reliably allow the clearing of the cache.
This is why they are broken out into separate tools. See
https://github.com/pydanny/cached-property/issues/16.

Credits
--------

* Pip, Django, Werkzueg, Bottle, Pyramid, and Zope for having their own implementations. This package originally used an implementation that matched the Bottle version.
* Reinout Van Rees for pointing out the `cached_property` decorator to me.
* My awesome wife `@audreyr`_ who created `cookiecutter`_, which meant rolling this out took me just 15 minutes.
* @tinche for pointing out the threading issue and providing a solution.
* @bcho for providing the time-to-expire feature

.. _`@audreyr`: https://github.com/audreyr
.. _`cookiecutter`: https://github.com/audreyr/cookiecutter

Support This Project
---------------------------

This project is maintained by volunteers. Support their efforts by spreading the word about:

Django Crash Course
~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://cdn.shopify.com/s/files/1/0304/6901/files/Django-Crash-Course-300x436.jpg
   :name: Django Crash Course: Covers Django 3.0 and Python 3.8
   :align: center
   :alt: Django Crash Course
   :target: https://www.roygreenfeld.com/products/django-crash-course

Django Crash Course for Django 3.0 and Python 3.8 is the best cheese-themed Django reference in the universe!
