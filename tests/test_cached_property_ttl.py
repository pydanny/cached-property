# -*- coding: utf-8 -*-

"""
test_threaded_cache_property.py
----------------------------------

Tests for `cached-property` module, cached_property_with_ttl.
Tests for `cached-property` module, threaded_cache_property_with_ttl.
"""

import unittest
from freezegun import freeze_time
from time import sleep
from threading import Lock, Thread

from cached_property import (
    cached_property_with_ttl,
    threaded_cached_property_with_ttl
)


class TestCachedPropertyWithTTL(unittest.TestCase):

    def test_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total1 = 0
                self.total2 = 0

            @property
            def add_control(self):
                self.total1 += 1
                return self.total1

            @cached_property_with_ttl
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

        # Cannot expire the cache.
        with freeze_time("9999-01-01"):
            self.assertEqual(c.add_cached, 1)

        # It's customary for descriptors to return themselves if accessed
        # though the class, rather than through an instance.
        self.assertTrue(isinstance(Check.add_cached, cached_property_with_ttl))

    def test_reset_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total = 0

            @cached_property_with_ttl
            def add_cached(self):
                self.total += 1
                return self.total

        c = Check()

        # Resetting the cache before it is set is a no-op
        del c.add_cached

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

            @cached_property_with_ttl
            def add_cached(self):
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, None)

    def test_threads(self):
        """ How well does the standard cached_property implementation work with threads?
            Short answer: It doesn't! Use threaded_cached_property instead!
        """  # noqa

        class Check(object):

            def __init__(self):
                self.total = 0
                self.lock = Lock()

            @cached_property_with_ttl
            def add_cached(self):
                sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.total += 1
                return self.total

        c = Check()
        threads = []
        num_threads = 10
        for x in range(num_threads):
            thread = Thread(target=lambda: c.add_cached)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        # Threads means that caching is bypassed.
        self.assertNotEqual(c.add_cached, 1)

        # This assertion hinges on the fact the system executing the test can
        # spawn and start running num_threads threads within the sleep period
        # (defined in the Check class as 1 second). If num_threads were to be
        # massively increased (try 10000), the actual value returned would be
        # between 1 and num_threads, depending on thread scheduling and
        # preemption.
        self.assertEqual(c.add_cached, num_threads)

    def test_ttl_expiry(self):

        class Check(object):

            def __init__(self):
                self.total = 0

            @cached_property_with_ttl(ttl=100000)
            def add_cached(self):
                self.total += 1
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, 1)
        self.assertEqual(c.add_cached, 1)

        # Expire the cache.
        with freeze_time("9999-01-01"):
            self.assertEqual(c.add_cached, 2)
        self.assertEqual(c.add_cached, 2)


class TestThreadedCachedPropertyWithTTL(unittest.TestCase):

    def test_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total1 = 0
                self.total2 = 0

            @property
            def add_control(self):
                self.total1 += 1
                return self.total1

            @threaded_cached_property_with_ttl
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

            @threaded_cached_property_with_ttl
            def add_cached(self):
                self.total += 1
                return self.total

        c = Check()

        # Resetting the cache before it is set is a no-op
        del c.add_cached

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

            @threaded_cached_property_with_ttl
            def add_cached(self):
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, None)

    def test_threads(self):
        """ How well does this implementation work with threads?"""

        class Check(object):

            def __init__(self):
                self.total = 0
                self.lock = Lock()

            @threaded_cached_property_with_ttl
            def add_cached(self):
                sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
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

        self.assertEqual(c.add_cached, 1)
