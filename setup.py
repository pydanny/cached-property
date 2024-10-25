#!/usr/bin/env python

import os
import sys
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = "2.0.1"


def read(fname):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), fname), "r", "utf-8"
    ).read()


readme = read("README.md")
history = read("HISTORY.md")

if sys.argv[-1] == "publish":
    try:
        import wheel
        import twine
    except:  # Yes, this is not how we usually do try/except
        raise ImportError('Run "pip install wheel twine"')
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    os.system("git tag -a %s -m 'version %s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()

setup(
    name="cached-property",
    version=__version__,
    description="A decorator for caching properties in classes.",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    author="Daniel Roy Greenfeld",
    author_email="daniel@feldroy.com",
    url="https://github.com/pydanny/cached-property",
    py_modules=["cached_property"],
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords="cached-property",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
