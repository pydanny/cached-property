#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__version__ = '1.0.0'

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    os.system("git tag -a %s -m 'version %s'" % (__version__, __version__))
    os.system("git push --tags")
    sys.exit()

setup(
    name='cached-property',
    version=__version__,
    description='A cached-property for decorating methods in classes.',
    long_description=readme + '\n\n' + history,
    author='Daniel Greenfeld',
    author_email='pydanny@gmail.com',
    url='https://github.com/pydanny/cached-property',
    py_modules=['cached_property'],
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords='cached-property',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
