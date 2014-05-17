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

* Free software: BSD license
* Documentation: http://cached-property.rtfd.org.

Why?
-----

* Makes caching of time or computational expensive properties quick and easy.
* Because I got tired of copy/pasting this code from non-web project to non-web project.
* I needed something really simple that worked in Python 2 and 3.

How to use it
--------------

Define a class with an expensive property. Every time you stay there the 
price goes up by $50. I

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

    >>> m = Monopoly()
    >>> m.boardwalk
    550
    >>> m.boardwalk
    600

Let's convert the boardwalk property into a `cached_property`.


.. code-block:: python

    from cached_property import cached_property

    class Monopoly(object):

        def __init__(self):
            self.boardwalk_price = 500

        @property
        def cached_property(self):
            # Again, this is a silly example. Don't worry about it, this is
            #   just an example for clarity.
            self.boardwalk_price += 50
            return self.boardwalk_price

Now when we run it the price stays at $550. Why? because it's cached!:

.. code-block:: python

    >>> m = Monopoly()
    >>> m.boardwalk
    550
    >>> m.boardwalk
    550
    >>> m.boardwalk
    550

Credits
--------

* Django, Werkzueg, Bottle, and Zope for having their own implementations. This package uses the Django version.
* Reinout Van Rees for pointing out the cached_property decorator to me.
