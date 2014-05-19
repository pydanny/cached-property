===============================
cached-property
===============================

.. image:: https://badge.fury.io/py/cached-property.png
    :target: http://badge.fury.io/py/cached-property
    
.. image:: https://travis-ci.org/pydanny/cached-property.png?branch=master
        :target: https://travis-ci.org/pydanny/cached-property

.. image:: https://pypip.in/d/cached-property/badge.png
        :target: https://pypi.python.org/pypi/cached-property


A cached-property for decorating methods in classes.

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

Let's convert the boardwalk property into a `cached_property`.


.. code-block:: python

    from cached_property import cached_property

    class Monopoly(object):

        def __init__(self):
            self.boardwalk_price = 500

        @cached_property
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

Why doesn't the value of `monopoly.boardwalk` change? Because it's a **cached property**!

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
    >>> del m.boardwalk
    >>> # request the boardwalk property again
    >>> m.boardwalk
    600
    >>> m.boardwalk
    600

Warning
-------

This library currently doesn't work with threads. Please see https://github.com/pydanny/cached-property/issues/6.

Credits
--------

* Pip, Django, Werkzueg, Bottle, Pyramid, and Zope for having their own implementations. This package uses an implementation that matches the Bottle version.
* Reinout Van Rees for pointing out the `cached_property` decorator to me.
* My awesome wife `@audreyr`_ who created `cookiecutter`_, which meant rolling this out took me just 15 minutes.

.. _`@audreyr`: https://github.com/audreyr
.. _`cookiecutter`: https://github.com/audreyr/cookiecutter