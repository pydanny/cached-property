# -*- coding: utf-8 -*-

import platform
import time
import unittest
from threading import Lock, Thread
from freezegun import freeze_time

import property_cached as cached_property


def CheckFactory(cached_property_decorator, threadsafe=False):
    """
    Create dynamically a Check class whose add_cached method is decorated by
    the cached_property_decorator.
    """

    class Check(object):
        def __init__(self):
            self.control_total = 0
            self.cached_total = 0
            self.lock = Lock()

        @property
        def add_control(self):
            self.control_total += 1
            return self.control_total

        @cached_property_decorator
        def add_cached(self):
            """A cached adder.
            """
            if threadsafe:
                time.sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.cached_total += 1
            else:
                self.cached_total += 1

            return self.cached_total

        def run_threads(self, num_threads):
            threads = []
            for _ in range(num_threads):
                thread = Thread(target=lambda: self.add_cached)
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    return Check


class TestCachedProperty(unittest.TestCase):
    """Tests for cached_property"""

    cached_property_factory = cached_property.cached_property

    def assert_control(self, check, expected):
        """
        Assert that both `add_control` and 'control_total` equal `expected`
        """
        self.assertEqual(check.add_control, expected)
        self.assertEqual(check.control_total, expected)

    def assert_cached(self, check, expected):
        """
        Assert that both `add_cached` and 'cached_total` equal `expected`
        """
        self.assertEqual(check.add_cached, expected)
        self.assertEqual(check.cached_total, expected)

    def test_magic_attributes(self):
        Check = CheckFactory(self.cached_property_factory)
        self.assertEqual(Check.add_cached.__doc__.strip(), "A cached adder.")
        self.assertEqual(Check.add_cached.__name__.strip(), "add_cached")
        self.assertEqual(Check.add_cached.__module__, __name__)

    def test_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()

        # The control shows that we can continue to add 1
        self.assert_control(check, 1)
        self.assert_control(check, 2)

        # The cached version demonstrates how nothing is added after the first
        self.assert_cached(check, 1)
        self.assert_cached(check, 1)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            self.assert_cached(check, 1)

        # Typically descriptors return themselves if accessed though the class
        # rather than through an instance.
        self.assertTrue(isinstance(Check.add_cached, self.cached_property_factory))

    def test_reset_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()

        # Run standard cache assertion
        self.assert_cached(check, 1)
        self.assert_cached(check, 1)

        # Clear the cache
        del check.add_cached

        # Value is cached again after the next access
        self.assert_cached(check, 2)
        self.assert_cached(check, 2)

    def test_none_cached_property(self):
        class Check(object):
            def __init__(self):
                self.cached_total = None

            @self.cached_property_factory
            def add_cached(self):
                return self.cached_total

        self.assert_cached(Check(), None)

    def test_set_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()
        check.add_cached = "foo"
        self.assertEqual(check.add_cached, "foo")
        self.assertEqual(check.cached_total, 0)

    def test_threads(self):
        Check = CheckFactory(self.cached_property_factory, threadsafe=True)
        check = Check()
        num_threads = 5

        # cached_property_with_ttl is *not* thread-safe!
        check.run_threads(num_threads)
        # This assertion hinges on the fact the system executing the test can
        # spawn and start running num_threads threads within the sleep period
        # (defined in the Check class as 1 second). If num_threads were to be
        # massively increased (try 10000), the actual value returned would be
        # between 1 and num_threads, depending on thread scheduling and
        # preemption.
        self.assert_cached(check, num_threads)
        self.assert_cached(check, num_threads)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            check.run_threads(num_threads)
            self.assert_cached(check, num_threads)
            self.assert_cached(check, num_threads)

    @unittest.skipUnless(platform.python_implementation() == "CPython",
                         "unknow garbage collection mechanism")
    def test_garbage_collection(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()
        check.add_cached = "foo"

        # check the instance is in the cache
        self.assertIn(check, Check.add_cached.cache)
        # remove the only reference to the Check instance
        del check
        # make sure the cache of the deleted object was removed
        self.assertEqual(Check.add_cached.cache, {})

    def test_object_independent(self):
        Check = CheckFactory(self.cached_property_factory)
        check1 = Check()
        check2 = Check()

        self.assert_cached(check1, 1)
        self.assert_cached(check1, 1)
        self.assert_cached(check2, 1)
        self.assert_cached(check2, 1)

        del check1.add_cached

        self.assert_cached(check1, 2)
        self.assert_cached(check1, 2)
        self.assert_cached(check2, 1)
        self.assert_cached(check2, 1)


class TestThreadedCachedProperty(TestCachedProperty):
    """Tests for threaded_cached_property"""

    cached_property_factory = cached_property.threaded_cached_property

    def test_threads(self):
        Check = CheckFactory(self.cached_property_factory, threadsafe=True)
        check = Check()
        num_threads = 5

        # threaded_cached_property_with_ttl is thread-safe
        check.run_threads(num_threads)
        self.assert_cached(check, 1)
        self.assert_cached(check, 1)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            check.run_threads(num_threads)
            self.assert_cached(check, 1)
            self.assert_cached(check, 1)


class TestCachedPropertyWithTTL(TestCachedProperty):
    """Tests for cached_property_with_ttl"""

    cached_property_factory = cached_property.cached_property_with_ttl

    def test_ttl_expiry(self):
        Check = CheckFactory(self.cached_property_factory(ttl=100000))
        check = Check()

        # Run standard cache assertion
        self.assert_cached(check, 1)
        self.assert_cached(check, 1)

        # The cache expires in the future
        with freeze_time("9999-01-01"):
            self.assert_cached(check, 2)
            self.assert_cached(check, 2)

        # Things are not reverted when we are back to the present
        self.assert_cached(check, 2)
        self.assert_cached(check, 2)

    def test_threads_ttl_expiry(self):
        Check = CheckFactory(self.cached_property_factory(ttl=100000), threadsafe=True)
        check = Check()
        num_threads = 5

        # Same as in test_threads
        check.run_threads(num_threads)
        self.assert_cached(check, num_threads)
        self.assert_cached(check, num_threads)

        # The cache expires in the future
        with freeze_time("9999-01-01"):
            check.run_threads(num_threads)
            self.assert_cached(check, 2 * num_threads)
            self.assert_cached(check, 2 * num_threads)

        # Things are not reverted when we are back to the present
        self.assert_cached(check, 2 * num_threads)
        self.assert_cached(check, 2 * num_threads)


class TestThreadedCachedPropertyWithTTL(
    TestThreadedCachedProperty, TestCachedPropertyWithTTL
):
    """Tests for threaded_cached_property_with_ttl"""

    cached_property_factory = cached_property.threaded_cached_property_with_ttl

    def test_threads_ttl_expiry(self):
        Check = CheckFactory(self.cached_property_factory(ttl=100000), threadsafe=True)
        check = Check()
        num_threads = 5

        # Same as in test_threads
        check.run_threads(num_threads)
        self.assert_cached(check, 1)
        self.assert_cached(check, 1)

        # The cache expires in the future
        with freeze_time("9999-01-01"):
            check.run_threads(num_threads)
            self.assert_cached(check, 2)
            self.assert_cached(check, 2)

        # Things are not reverted when we are back to the present
        self.assert_cached(check, 2)
        self.assert_cached(check, 2)
