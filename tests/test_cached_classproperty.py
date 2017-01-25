# -*- coding: utf-8 -*-

import time
import unittest
from threading import Lock, Thread
from freezegun import freeze_time

import cached_property


def CheckFactory(cached_property_decorator, threadsafe=False):
    """
    Create dynamically a Check class whose add_cached method is decorated by
    the cached_property_decorator.
    """

    class Check(object):

        cached_total = 0
        lock = Lock()

        @cached_property_decorator
        def add_cached(cls):
            if threadsafe:
                time.sleep(1)
                # Need to guard this since += isn't atomic.
                with cls.lock:
                    cls.cached_total += 1
            else:
                cls.cached_total += 1
            return cls.cached_total

        def run_threads(self, num_threads):
            threads = []
            for _ in range(num_threads):
                thread = Thread(target=lambda: self.add_cached)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    return Check


class TestCachedClassProperty(unittest.TestCase):
    """Tests for cached_property"""

    cached_property_factory = cached_property.cached_classproperty

    def assert_cached(self, check, expected):
        """
        Assert that both `add_cached` and 'cached_total` equal `expected`
        """
        self.assertEqual(check.add_cached, expected)
        self.assertEqual(check.cached_total, expected)

    def test_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)

        # The cached version demonstrates how nothing is added after the first
        self.assert_cached(Check(), 1)
        self.assert_cached(Check(), 1)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            self.assert_cached(Check(), 1)

    def test_none_cached_property(self):
        class Check(object):

            cached_total = None

            @self.cached_property_factory
            def add_cached(cls):
                return cls.cached_total

        self.assert_cached(Check(), None)

    def test_set_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        Check.add_cached = 'foo'
        self.assertEqual(Check().add_cached, 'foo')
        self.assertEqual(Check().cached_total, 0)

    def test_threads(self):
        Check = CheckFactory(self.cached_property_factory, threadsafe=True)
        num_threads = 5

        # cached_property_with_ttl is *not* thread-safe!
        Check().run_threads(num_threads)
        # This assertion hinges on the fact the system executing the test can
        # spawn and start running num_threads threads within the sleep period
        # (defined in the Check class as 1 second). If num_threads were to be
        # massively increased (try 10000), the actual value returned would be
        # between 1 and num_threads, depending on thread scheduling and
        # preemption.
        self.assert_cached(Check(), num_threads)
        self.assert_cached(Check(), num_threads)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            Check().run_threads(num_threads)
            self.assert_cached(Check(), num_threads)
            self.assert_cached(Check(), num_threads)
