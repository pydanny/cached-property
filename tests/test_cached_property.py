# -*- coding: utf-8 -*-

"""Tests for cached_property and threaded_cached_property"""

from time import sleep
from threading import Lock, Thread
import unittest

from cached_property import cached_property, threaded_cached_property


class TestCachedProperty(unittest.TestCase):
    """Tests for cached_property"""

    cached_property_factory = cached_property

    def test_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total1 = 0
                self.total2 = 0

            @property
            def add_control(self):
                self.total1 += 1
                return self.total1

            @self.cached_property_factory
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
        self.assertEqual(c.total2, 1)

        # It's customary for descriptors to return themselves if accessed
        # though the class, rather than through an instance.
        self.assertTrue(isinstance(Check.add_cached, self.cached_property_factory))

    def test_reset_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total = 0

            @self.cached_property_factory
            def add_cached(self):
                self.total += 1
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, 1)
        self.assertEqual(c.add_cached, 1)
        self.assertEqual(c.total, 1)

        # Reset the cache.
        del c.add_cached
        self.assertEqual(c.add_cached, 2)
        self.assertEqual(c.add_cached, 2)
        self.assertEqual(c.total, 2)

    def test_none_cached_property(self):

        class Check(object):

            def __init__(self):
                self.total = None

            @self.cached_property_factory
            def add_cached(self):
                return self.total

        c = Check()

        # Run standard cache assertion
        self.assertEqual(c.add_cached, None)
        self.assertEqual(c.total, None)

    def test_threads(self):
        """
        How well does the standard cached_property implementation work with
        threads? It doesn't, use threaded_cached_property instead!
        """
        num_threads = 10
        check = self._run_threads(num_threads)
        # Threads means that caching is bypassed.
        # This assertion hinges on the fact the system executing the test can
        # spawn and start running num_threads threads within the sleep period
        # (defined in the Check class as 1 second). If num_threads were to be
        # massively increased (try 10000), the actual value returned would be
        # between 1 and num_threads, depending on thread scheduling and
        # preemption.
        self.assertEqual(check.add_cached, num_threads)
        self.assertEqual(check.total, num_threads)

    def _run_threads(self, num_threads):
        class Check(object):

            def __init__(self):
                self.total = 0
                self.lock = Lock()

            @self.cached_property_factory
            def add_cached(self):
                sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.total += 1
                return self.total

        c = Check()

        threads = []
        for _ in range(num_threads):
            thread = Thread(target=lambda: c.add_cached)
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()

        return c


class TestThreadedCachedProperty(TestCachedProperty):
    """Tests for threaded_cached_property"""

    cached_property_factory = threaded_cached_property

    def test_threads(self):
        """How well does this implementation work with threads?"""
        num_threads = 10
        check = self._run_threads(num_threads)
        self.assertEqual(check.add_cached, 1)
        self.assertEqual(check.total, 1)
