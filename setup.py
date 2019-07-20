#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import codecs

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = "1.5.1"


def read(fname):
    return codecs.open(
        os.path.join(os.path.dirname(__file__), fname), "r", "utf-8"
    ).read()


readme = read("README.rst")
history = read("HISTORY.rst").replace(".. :changelog:", "")

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    os.system("git tag -a %s -m 'version %s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()

setup(
    name="property-cached",
    version=__version__,
    description="A decorator for caching properties in classes (forked from cached-property).",
    long_description=readme + "\n\n" + history,
    author="Martin Larralde",
    author_email="martin.larralde@ens-paris-saclay.fr",
    url="https://github.com/althonos/property-cached",
    py_modules=["cached_property"],
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords=["cached-property"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
