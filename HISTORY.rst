.. :changelog:

History
-------

1.0.0 (2014-02-13)
++++++++++++++++++

* Added timed to expire feature to ``cached_property`` decorator.
* **Backwards incompatiblity**: Changed ``del monopoly.boardwalk`` to ``del monopoly['boardwalk']`` in order to support the new TTL feature.

0.1.5 (2014-05-20)
++++++++++++++++++

* Added threading support with new ``threaded_cached_property`` decorator
* Documented cache invalidation
* Updated credits
* Sourced the bottle implementation

0.1.4 (2014-05-17)
++++++++++++++++++

* Fix the dang-blarged py_modules argument.

0.1.3 (2014-05-17)
++++++++++++++++++

* Removed import of package into ``setup.py``

0.1.2 (2014-05-17)
++++++++++++++++++

* Documentation fixes. Not opening up a RTFD instance for this because it's so simple to use.

0.1.1 (2014-05-17)
++++++++++++++++++

* setup.py fix. Whoops!

0.1.0 (2014-05-17)
++++++++++++++++++

* First release on PyPI.
