#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = "1.5.2"


def read(fname):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), fname), "r", "utf-8"
    ).read()


readme = read("README.rst")
history = read("HISTORY.rst").replace(".. :changelog:", "")

if sys.argv[-1] == "publish":
    try:
        import wheel
        import twine
    except: # Yes, this is not how we usually do try/except
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
    long_description_content_type="text/x-rst",
    author="Daniel Greenfeld",
    author_email="pydanny@gmail.com",
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
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",     
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
