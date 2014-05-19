# -*- coding: utf-8 -*-

"""
tests.py
----------------------------------

Tests for `cached-property` module.
"""

from time import sleep
from threading import Thread
import unittest

from cached_property import cached_property


class TestCachedProperty(unittest.TestCase):

    def test_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total1 = 0
                self.total2 = 0

            @property
            def add_control(self):
                self.total1 += 1
                return self.total1

            @cached_property
            def add_cached(self):
                self.total2 += 1
                return self.total2

        c = Check()

        # The control shows that we can continue to add 1.
        self.assertEqual(c.add_control, 1)
        self.assertEqual(c.add_control, 2)

        # The cached version demonstrates how nothing new is added
        self.assertEqual(c.add_cached, 1)
        self.assertEqual(c.add_cached, 1)

    def test_reset_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total = 0

            @cached_property
            def add_cached(self):
                self.total += 1
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, 1)
        self.assertEqual(c.add_cached, 1)

        # Reset the cache.
        del c.add_cached
        self.assertEqual(c.add_cached, 2)
        self.assertEqual(c.add_cached, 2)

    def test_none_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total = None

            @cached_property
            def add_cached(self):
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, None)


class TestThreadingIssues(unittest.TestCase):

    def test_threads(self):
        """ How well does this implementation work with threads?"""

        class Check(object):

            def __init__(self):
                self.total = 0

            @cached_property
            def add_cached(self):
                sleep(1)
                self.total += 1
                return self.total

        c = Check()
        threads = []
        for x in range(10):
            thread = Thread(target=lambda: c.add_cached)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # TODO: This assertion should be working.
        # See https://github.com/pydanny/cached-property/issues/6
        # self.assertEqual(c.add_cached, 1)

        # TODO: This assertion should be failing.
        # See https://github.com/pydanny/cached-property/issues/6
        self.assertEqual(c.add_cached, 10)
