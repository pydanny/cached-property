===============================
cached-property
===============================

.. image:: https://badge.fury.io/py/cached-property.png
    :target: http://badge.fury.io/py/cached-property

.. image:: https://travis-ci.org/pydanny/cached-property.png?branch=master
        :target: https://travis-ci.org/pydanny/cached-property


A decorator for caching properties in classes.

Why?
-----

* Makes caching of time or computational expensive properties quick and easy.
* Because I got tired of copy/pasting this code from non-web project to non-web project.
* I needed something really simple that worked in Python 2 and 3.

How to use it
--------------

Let's define a class with an expensive property. Every time you stay there the 
price goes up by $50!

.. code-block:: python

    class Monopoly(object):

        def __init__(self):
            self.boardwalk_price = 500

        @property
        def boardwalk(self):
            # In reality, this might represent a database call or time 
            # intensive task like calling a third-party API.
            self.boardwalk_price += 50
            return self.boardwalk_price

Now run it:

.. code-block:: python

    >>> monopoly = Monopoly()
    >>> monopoly.boardwalk
    550
    >>> monopoly.boardwalk
    600

Let's convert the boardwalk property into a ``cachedproperty``.

.. code-block:: python

    from cached_property import cachedproperty

    class Monopoly(object):

        def __init__(self):
            self.boardwalk_price = 500

        @cachedproperty
        def boardwalk(self):
            # Again, this is a silly example. Don't worry about it, this is
            #   just an example for clarity.
            self.boardwalk_price += 50
            return self.boardwalk_price

Now when we run it the price stays at $550.

.. code-block:: python

    >>> monopoly = Monopoly()
    >>> monopoly.boardwalk
    550
    >>> monopoly.boardwalk
    550
    >>> monopoly.boardwalk
    550

Why doesn't the value of ``monopoly.boardwalk`` change? Because it's a **cached property**!

Invalidating the Cache
----------------------

Results of cached functions can be invalidated by outside forces. Let's demonstrate how to force the cache to invalidate:

.. code-block:: python

    >>> monopoly = Monopoly()
    >>> monopoly.boardwalk
    550
    >>> monopoly.boardwalk
    550
    >>> # invalidate the cache
    >>> del monopoly.boardwalk
    >>> # request the boardwalk property again
    >>> monopoly.boardwalk
    600
    >>> monopoly.boardwalk
    600

Working with Threads
---------------------

What if a whole bunch of people want to stay at Boardwalk all at once? This means using threads, which
unfortunately causes problems with the standard ``cachedproperty``. In this case, pass
``threadsafe=True``:

.. code-block:: python

    import threading

    from cached_property import cachedproperty

    class Monopoly(object):

        def __init__(self):
            self.boardwalk_price = 500
            self.lock = threading.Lock()

        @cachedproperty(threadsafe=True)
        def boardwalk(self):
            """
            threadsafe=True is really nice for when no one waits for other
            people to finish their turn and rudely start rolling dice and
            moving their pieces.
            """
            sleep(1)
            # Need to guard this since += isn't atomic.
            with self.lock:
                self.boardwalk_price += 50
            return self.boardwalk_price

Now use it:

.. code-block:: python

    >>> from threading import Thread
    >>> from monopoly import Monopoly
    >>> monopoly = Monopoly()
    >>> threads = []
    >>> for x in range(10):
    >>>     thread = Thread(target=lambda: monopoly.boardwalk)
    >>>     thread.start()
    >>>     threads.append(thread)

    >>> for thread in threads:
    >>>     thread.join()

    >>> self.assertEqual(m.boardwalk, 550)


Timing out the cache
--------------------

Sometimes you want the price of things to reset after a time. In such cases you
can pass ``ttl``:

.. code-block:: python

    import random
    from cached_property import cachedproperty

    class Monopoly(object):

        @cachedproperty(ttl=5) # cache invalidates after 5 seconds
        def dice(self):
            # I dare the reader to implement a game using this method of 'rolling dice'.
            return random.randint(2,12)

Now use it:

.. code-block:: python

    >>> monopoly = Monopoly()
    >>> monopoly.dice
    10
    >>> monopoly.dice
    10
    >>> from time import sleep
    >>> sleep(6) # Sleeps long enough to expire the cache
    >>> monopoly.dice
    3
    >>> monopoly.dice
    3


Credits
--------

* Pip, Django, Werkzueg, Bottle, Pyramid, and Zope for having their own implementations. This package uses an implementation that matches the Bottle version.
* Reinout Van Rees for pointing out the `cached_property` decorator to me.
* My awesome wife `@audreyr`_ who created `cookiecutter`_, which meant rolling this out took me just 15 minutes.
* @tinche for pointing out the threading issue and providing a solution.
* @bcho for providing the time-to-expire feature

.. _`@audreyr`: https://github.com/audreyr
.. _`cookiecutter`: https://github.com/audreyr/cookiecutter
