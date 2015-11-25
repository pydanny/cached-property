.. :changelog:

History
-------

1.3.0 (2015-11-24)
++++++++++++++++++

* Added official support for Python 3, thanks to @pydanny
* Removed confusingly placed lock from example, thanks to @ionelmc
* Corrected invalidation cache documentation, thanks to @proofit404

1.2.0 (2015-04-28)
++++++++++++++++++

* Overall code and test refactoring, thanks to @gsakkis
* Allow the del statement for resetting cached properties with ttl instead of del obj._cache[attr], thanks to @gsakkis.
* Uncovered a bug in PyPy, https://bitbucket.org/pypy/pypy/issue/2033/attributeerror-object-attribute-is-read, thanks to @gsakkis
* Fixed threaded_cached_property_with_ttl to actually be thread-safe, thanks to @gsakkis

1.1.0 (2015-04-04)
++++++++++++++++++

* Regression: As the cache was not always clearing, we've broken out the time to expire feature to its own set of specific tools, thanks to @pydanny
* Fixed typo in README, thanks to @zoidbergwill

1.0.0 (2015-02-13)
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
