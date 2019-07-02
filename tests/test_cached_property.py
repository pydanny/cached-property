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
        def __init__(self):
            self.control_total = 0
            self.cached_total = 0
            self.protected_cached_total = 0
            self.private_cached_total = 0
            self.magic_cached_total = 0
            self.lock = Lock()

        @property
        def add_control(self):
            self.control_total += 1
            return self.control_total

        @cached_property_decorator
        def add_cached(self):
            if threadsafe:
                time.sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.cached_total += 1
            else:
                self.cached_total += 1

            return self.cached_total

        @cached_property_decorator
        def _protected_add_cached(self):
            if threadsafe:
                time.sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.protected_cached_total += 1
            else:
                self.protected_cached_total += 1

            return self.protected_cached_total

        @cached_property_decorator
        def __private_add_cached(self):
            if threadsafe:
                time.sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.private_cached_total += 1
            else:
                self.private_cached_total += 1

            return self.private_cached_total

        @cached_property_decorator
        def __magic_add_cached__(self):
            if threadsafe:
                time.sleep(1)
                # Need to guard this since += isn't atomic.
                with self.lock:
                    self.magic_cached_total += 1
            else:
                self.magic_cached_total += 1

            return self.magic_cached_total

        def run_threads(self, num_threads, target_attr="add_cached"):
            threads = []
            for _ in range(num_threads):
                thread = Thread(target=lambda: getattr(self, target_attr))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

    return Check


class TestCachedProperty(unittest.TestCase):
    """Tests for cached_property"""

    cached_property_factory = cached_property.cached_property
    cached_attrs = (
        ("add_cached", "cached_total"),
        ("_protected_add_cached", "protected_cached_total"),
        ("_Check__private_add_cached", "private_cached_total"),
        ("__magic_add_cached__", "magic_cached_total"),
    )

    def assert_control(self, check, expected):
        """
        Assert that both `add_control` and 'control_total` equal `expected`
        """
        self.assertEqual(check.add_control, expected)
        self.assertEqual(check.control_total, expected)

    def assert_cached(self, check, expected, cached_attr, total_attr):
        """
        Assert that both `add_cached` and 'cached_total` equal `expected`
        """
        self.assertEqual(getattr(check, cached_attr), expected)
        self.assertEqual(getattr(check, total_attr), expected)

    def test_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()

        # The control shows that we can continue to add 1
        self.assert_control(check, 1)
        self.assert_control(check, 2)

        # The cached version demonstrates how nothing is added after the first
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 1, cached_attr, total_attr)
            self.assert_cached(check, 1, cached_attr, total_attr)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            for cached_attr, total_attr in self.cached_attrs:
                self.assert_cached(check, 1, cached_attr, total_attr)

        # Typically descriptors return themselves if accessed though the class
        # rather than through an instance.
        for cached_attr, _ in self.cached_attrs:
            self.assertTrue(
                isinstance(getattr(Check, cached_attr), self.cached_property_factory)
            )

    def test_reset_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()

        # Run standard cache assertion
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 1, cached_attr, total_attr)
            self.assert_cached(check, 1, cached_attr, total_attr)

        # Clear the cache
        for cached_attr, total_attr in self.cached_attrs:
            delattr(check, cached_attr)

        # Value is cached again after the next access
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 2, cached_attr, total_attr)
            self.assert_cached(check, 2, cached_attr, total_attr)

    def test_none_cached_property(self):
        class Check(object):
            def __init__(self):
                self.cached_total = None

            @self.cached_property_factory
            def add_cached(self):
                return self.cached_total

        self.assert_cached(Check(), None, "add_cached", "cached_total")

    def test_set_cached_property(self):
        Check = CheckFactory(self.cached_property_factory)
        check = Check()

        for cached_attr, total_attr in self.cached_attrs:
            setattr(check, cached_attr, "foo")
            self.assertEqual(getattr(check, cached_attr), "foo")
            self.assertEqual(getattr(check, total_attr), 0)

    def test_threads(self):
        Check = CheckFactory(self.cached_property_factory, threadsafe=True)
        check = Check()
        num_threads = 5

        # cached_property_with_ttl is *not* thread-safe!
        for cached_attr, _ in self.cached_attrs:
            check.run_threads(num_threads, target_attr=cached_attr)

        # This assertion hinges on the fact the system executing the test can
        # spawn and start running num_threads threads within the sleep period
        # (defined in the Check class as 1 second). If num_threads were to be
        # massively increased (try 10000), the actual value returned would be
        # between 1 and num_threads, depending on thread scheduling and
        # preemption.
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, num_threads, cached_attr, total_attr)
            self.assert_cached(check, num_threads, cached_attr, total_attr)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            for cached_attr, _ in self.cached_attrs:
                check.run_threads(num_threads, target_attr=cached_attr)

            for cached_attr, total_attr in self.cached_attrs:
                self.assert_cached(check, num_threads, cached_attr, total_attr)
                self.assert_cached(check, num_threads, cached_attr, total_attr)


class TestThreadedCachedProperty(TestCachedProperty):
    """Tests for threaded_cached_property"""

    cached_property_factory = cached_property.threaded_cached_property

    def test_threads(self):
        Check = CheckFactory(self.cached_property_factory, threadsafe=True)
        check = Check()
        num_threads = 5

        # threaded_cached_property_with_ttl is thread-safe
        for cached_attr, _ in self.cached_attrs:
            check.run_threads(num_threads, target_attr=cached_attr)

        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 1, cached_attr, total_attr)
            self.assert_cached(check, 1, cached_attr, total_attr)

        # The cache does not expire
        with freeze_time("9999-01-01"):
            for cached_attr, _ in self.cached_attrs:
                check.run_threads(num_threads, target_attr=cached_attr)

            for cached_attr, total_attr in self.cached_attrs:
                self.assert_cached(check, 1, cached_attr, total_attr)
                self.assert_cached(check, 1, cached_attr, total_attr)


class TestCachedPropertyWithTTL(TestCachedProperty):
    """Tests for cached_property_with_ttl"""

    cached_property_factory = cached_property.cached_property_with_ttl

    def test_ttl_expiry(self):
        factory = lambda func: self.cached_property_factory(ttl=100000)(func)
        Check = CheckFactory(factory)
        check = Check()

        # Run standard cache assertion
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 1, cached_attr, total_attr)
            self.assert_cached(check, 1, cached_attr, total_attr)

        # The cache expires in the future
        with freeze_time("9999-01-01"):
            for cached_attr, total_attr in self.cached_attrs:
                self.assert_cached(check, 2, cached_attr, total_attr)
                self.assert_cached(check, 2, cached_attr, total_attr)

        # Things are not reverted when we are back to the present
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 2, cached_attr, total_attr)
            self.assert_cached(check, 2, cached_attr, total_attr)

    def test_threads_ttl_expiry(self):
        factory = lambda func: self.cached_property_factory(ttl=100000)(func)
        Check = CheckFactory(factory, threadsafe=True)
        check = Check()
        num_threads = 5

        # Same as in test_threads
        for cached_attr, _ in self.cached_attrs:
            check.run_threads(num_threads, target_attr=cached_attr)

        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, num_threads, cached_attr, total_attr)
            self.assert_cached(check, num_threads, cached_attr, total_attr)

        # The cache expires in the future
        with freeze_time("9999-01-01"):
            for cached_attr, _ in self.cached_attrs:
                check.run_threads(num_threads, target_attr=cached_attr)

            for cached_attr, total_attr in self.cached_attrs:
                self.assert_cached(check, 2 * num_threads, cached_attr, total_attr)
                self.assert_cached(check, 2 * num_threads, cached_attr, total_attr)

        # Things are not reverted when we are back to the present
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 2 * num_threads, cached_attr, total_attr)
            self.assert_cached(check, 2 * num_threads, cached_attr, total_attr)


class TestThreadedCachedPropertyWithTTL(
    TestThreadedCachedProperty, TestCachedPropertyWithTTL
):
    """Tests for threaded_cached_property_with_ttl"""

    cached_property_factory = cached_property.threaded_cached_property_with_ttl

    def test_threads_ttl_expiry(self):
        factory = lambda func: self.cached_property_factory(ttl=100000)(func)
        Check = CheckFactory(factory, threadsafe=True)
        check = Check()
        num_threads = 5

        # Same as in test_threads
        for cached_attr, _ in self.cached_attrs:
            check.run_threads(num_threads, target_attr=cached_attr)

        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 1, cached_attr, total_attr)
            self.assert_cached(check, 1, cached_attr, total_attr)

        # The cache expires in the future
        with freeze_time("9999-01-01"):
            for cached_attr, _ in self.cached_attrs:
                check.run_threads(num_threads, target_attr=cached_attr)

            for cached_attr, total_attr in self.cached_attrs:
                self.assert_cached(check, 2, cached_attr, total_attr)
                self.assert_cached(check, 2, cached_attr, total_attr)

        # Things are not reverted when we are back to the present
        for cached_attr, total_attr in self.cached_attrs:
            self.assert_cached(check, 2, cached_attr, total_attr)
            self.assert_cached(check, 2, cached_attr, total_attr)
