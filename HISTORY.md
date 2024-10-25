# History

## 2.0.1 (2024-10-25)

* Via `python_requires` specifies that cached_property is for Python version 3.8 or higher
* Officiall drop support for Python 2.6

## 2.0.0 (2024-10-25)

* Remove support for Python versions < 3.8
* Add formal support for Python versions up to 3.13
* Switch to Markdown for docs
* Migrate from black to ruff

## 1.5.2 (2020-09-21)

* Add formal support for Python 3.8
* Remove formal support for Python 3.4
* Switch from Travis to GitHub actions
* Made tests pass flake8 for Python 2.7

## 1.5.1 (2018-08-05)

* Added formal support for Python 3.7
* Removed formal support for Python 3.3

## 1.4.3  (2018-06-14)

* Catch SyntaxError from asyncio import on older versions of Python, thanks to @asottile

## 1.4.2 (2018-04-08)

* Really fixed tests, thanks to @pydanny

## 1.4.1 (2018-04-08)

* Added conftest.py to manifest so tests work properly off the tarball, thanks to @dotlambda
* Ensured new asyncio tests didn't break Python 2.7 builds on Debian, thanks to @pydanny
* Code formatting via black, thanks to @pydanny and @ambv

## 1.4.0 (2018-02-25)

* Added asyncio support, thanks to @vbraun
* Remove Python 2.6 support, whose end of life was 5 years ago, thanks to @pydanny

## 1.3.1 (2017-09-21)

* Validate for Python 3.6

## 1.3.0 (2015-11-24)

* Drop some non-ASCII characters from HISTORY.rst, thanks to @AdamWill
* Added official support for Python 3.5, thanks to @pydanny and @audreyr
* Removed confusingly placed lock from example, thanks to @ionelmc
* Corrected invalidation cache documentation, thanks to @proofit404
* Updated to latest Travis-CI environment, thanks to @audreyr

## 1.2.0 (2015-04-28)

* Overall code and test refactoring, thanks to @gsakkis
* Allow the del statement for resetting cached properties with ttl instead of del obj._cache[attr], thanks to @gsakkis.
* Uncovered a bug in PyPy, https://bitbucket.org/pypy/pypy/issue/2033/attributeerror-object-attribute-is-read, thanks to @gsakkis
* Fixed threaded_cached_property_with_ttl to actually be thread-safe, thanks to @gsakkis

## 1.1.0 (2015-04-04)

* Regression: As the cache was not always clearing, we've broken out the time to expire feature to its own set of specific tools, thanks to @pydanny
* Fixed typo in README, thanks to @zoidbergwill

## 1.0.0 (2015-02-13)

* Added timed to expire feature to `cached_property` decorator.
* **Backwards incompatibility**: Changed `del monopoly.boardwalk` to `del monopoly['boardwalk']` in order to support the new TTL feature.

## 0.1.5 (2014-05-20)

* Added threading support with new `threaded_cached_property` decorator
* Documented cache invalidation
* Updated credits
* Sourced the bottle implementation

## 0.1.4 (2014-05-17)

* Fix the dang-blarged py_modules argument.

## 0.1.3 (2014-05-17)

* Removed import of package into `setup.py`

## 0.1.2 (2014-05-17)

* Documentation fixes. Not opening up a RTFD instance for this because it's so simple to use.

## 0.1.1 (2014-05-17)

* setup.py fix. Whoops!

## 0.1.0 (2014-05-17)

* First release on PyPI.
