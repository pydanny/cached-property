import pickle
import gc
import threading
import unittest
import weakref
from unittest.mock import patch

import cached_property as cp


DECORATORS = (cp.threaded_cached_property, cp.threaded_cached_property_with_ttl)


class Unhashable:
    __hash__ = None

    def __init__(self):
        self.calls = 0

    @cp.threaded_cached_property
    def value(self):
        self.calls += 1
        return 7


class NoWeakref:
    __slots__ = ('__dict__',)


class UnhashableTTL:
    __hash__ = None

    def __init__(self):
        self.calls = 0

    @cp.threaded_cached_property_with_ttl
    def value(self):
        self.calls += 1
        return 7


class TestInstanceLocks(unittest.TestCase):
    def test_different_instances_interleave_with_real_locks(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                entered, release, second_done = threading.Event(), threading.Event(), threading.Event()
                values, errors = [], []

                class C:
                    def __init__(self, first):
                        self.first = first

                    @decorator
                    def value(self):
                        if self.first:
                            entered.set()
                            if not release.wait(5):
                                raise AssertionError('cleanup timeout')
                        return 7

                def read(first):
                    try:
                        values.append(C(first).value)
                    except BaseException as error:
                        errors.append(error)
                    finally:
                        if not first:
                            second_done.set()

                threads = [threading.Thread(target=read, args=(first,)) for first in (True, False)]
                threads[0].start()
                try:
                    self.assertTrue(entered.wait(5))
                    threads[1].start()
                    self.assertTrue(second_done.wait(5), 'second instance blocked until first release')
                    self.assertEqual([7], values)
                finally:
                    release.set()
                    for thread in threads:
                        if thread.ident is not None:
                            thread.join(5)
                self.assertTrue(all(not thread.is_alive() for thread in threads))
                self.assertEqual([], errors)
                self.assertEqual([7, 7], values)
                self.assertEqual({}, C.value._active_locks)

    def test_class_access_does_not_register(self):
        for decorator in DECORATORS:
            descriptor = decorator(lambda obj: 7)
            self.assertIs(descriptor, descriptor.__get__(None, NoWeakref))
            self.assertEqual({}, descriptor._active_locks)

    def test_waiter_and_later_arrival_share_one_active_lock(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                first_entered, first_release = threading.Event(), threading.Event()
                waiter_started, waiter_acquired = threading.Event(), threading.Event()
                waiter_release, later_started = threading.Event(), threading.Event()
                values, errors, created = [], [], []

                class C:
                    calls = 0

                    @decorator
                    def value(self):
                        self.calls += 1
                        first_entered.set()
                        if not first_release.wait(5):
                            raise AssertionError('first getter timeout')
                        return 7

                instance, descriptor = C(), C.value
                real_lock_factory = threading.RLock

                class ControlledLock:
                    def __init__(self):
                        self.real = real_lock_factory()
                        created.append(self)

                    def __enter__(self):
                        name = threading.current_thread().name
                        if name == 'waiter':
                            waiter_started.set()
                        if name == 'later':
                            later_started.set()
                        self.real.acquire()
                        if name == 'waiter':
                            waiter_acquired.set()
                            if not waiter_release.wait(5):
                                self.real.release()
                                raise AssertionError('waiter timeout')
                        return self

                    def __exit__(self, *exc):
                        self.real.release()

                def read():
                    try:
                        values.append(descriptor.__get__(instance, C))
                    except BaseException as error:
                        errors.append(error)

                threads = [threading.Thread(target=read, name=name)
                           for name in ('first', 'waiter', 'later')]
                with patch.object(cp.threading, 'RLock', ControlledLock):
                    try:
                        threads[0].start()
                        self.assertTrue(first_entered.wait(5))
                        threads[1].start()
                        self.assertTrue(waiter_started.wait(5))
                        with descriptor.lock:
                            self.assertEqual(2, descriptor._active_locks[id(instance)][2])
                        first_release.set()
                        threads[0].join(5)
                        self.assertTrue(waiter_acquired.wait(5))
                        threads[2].start()
                        self.assertTrue(later_started.wait(5))
                        with descriptor.lock:
                            self.assertEqual(2, descriptor._active_locks[id(instance)][2])
                        self.assertEqual(1, len(created))
                    finally:
                        first_release.set()
                        waiter_release.set()
                        for thread in threads:
                            if thread.ident is not None:
                                thread.join(5)
                self.assertTrue(all(not thread.is_alive() for thread in threads))
                self.assertEqual([], errors)
                self.assertEqual([7, 7, 7], values)
                self.assertEqual(1, instance.calls)
                self.assertEqual({}, descriptor._active_locks)

    def test_acquisition_failure_releases_registry_entry(self):
        class InterruptedLock:
            def __enter__(self):
                raise KeyboardInterrupt('interrupted acquisition')

            def __exit__(self, *exc):
                raise AssertionError('unacquired lock must not be released')

        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                descriptor = decorator(lambda obj: 7)
                instance = NoWeakref()
                with patch.object(cp.threading, 'RLock', InterruptedLock):
                    with self.assertRaisesRegex(KeyboardInterrupt, 'interrupted acquisition'):
                        descriptor.__get__(instance, NoWeakref)
                self.assertEqual({}, descriptor._active_locks)
                self.assertEqual({}, instance.__dict__)
                self.assertEqual(7, descriptor.__get__(instance, NoWeakref))
                self.assertEqual({}, descriptor._active_locks)

    def test_finished_getter_does_not_retain_instance(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                class C:
                    @decorator
                    def value(self):
                        return 7

                instance = C()
                ref = weakref.ref(instance)
                self.assertEqual(7, instance.value)
                self.assertEqual({}, C.value._active_locks)
                del instance
                gc.collect()
                self.assertIsNone(ref())

    def test_independent_instances_do_not_hold_descriptor_lock_in_getter(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                entered = threading.Event()
                release = threading.Event()
                results, errors = [], []

                class C:
                    def __init__(self, first):
                        self.first = first

                    @decorator
                    def value(self):
                        if self.first:
                            entered.set()
                            if not release.wait(5):
                                raise AssertionError('first getter cleanup timed out')
                        return 7

                descriptor = C.value
                original_lock = descriptor.lock

                class ProbeLock:
                    def __enter__(self):
                        if threading.current_thread().name == 'second-instance':
                            if not original_lock.acquire(blocking=False):
                                raise AssertionError('different instance blocked by getter-held descriptor lock')
                        else:
                            original_lock.acquire()
                        return self

                    def __exit__(self, *exc):
                        original_lock.release()

                descriptor.lock = ProbeLock()

                def read(instance):
                    try:
                        results.append(instance.value)
                    except BaseException as error:
                        errors.append(error)

                first = threading.Thread(target=read, args=(C(True),))
                second = threading.Thread(target=read, args=(C(False),), name='second-instance')
                first.start()
                try:
                    self.assertTrue(entered.wait(5))
                    second.start()
                    second.join(5)
                    self.assertFalse(second.is_alive(), 'independent getter did not finish')
                finally:
                    release.set()
                    first.join(5)
                    if second.ident is not None:
                        second.join(5)
                self.assertFalse(first.is_alive())
                self.assertEqual([], errors)
                self.assertEqual([7, 7], results)

    def test_same_instance_is_computed_once(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                start = threading.Barrier(5)
                values, errors = [], []

                class C:
                    calls = 0

                    @decorator
                    def value(self):
                        self.calls += 1
                        return 7

                instance = C()

                def read():
                    try:
                        start.wait(5)
                        values.append(instance.value)
                    except BaseException as error:
                        errors.append(error)

                threads = [threading.Thread(target=read) for _ in range(5)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join(5)
                self.assertTrue(all(not thread.is_alive() for thread in threads))
                self.assertEqual([], errors)
                self.assertEqual([7] * 5, values)
                self.assertEqual(1, instance.calls)

    def test_exception_retry_and_reentrant_getter(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                class C:
                    calls = 0

                    @decorator
                    def value(self):
                        self.calls += 1
                        if self.calls == 1:
                            raise ValueError('retry me')
                        if self.calls == 2:
                            return self.value
                        return 7

                instance = C()
                with self.assertRaisesRegex(ValueError, 'retry me'):
                    instance.value
                self.assertEqual({}, C.value._active_locks)
                self.assertEqual(7, instance.value)
                self.assertEqual(7, instance.value)
                self.assertEqual(3, instance.calls)
                self.assertEqual({}, C.value._active_locks)

    def test_unhashable_and_pickle_without_lock_pollution(self):
        for cls in (Unhashable, UnhashableTTL):
            with self.subTest(cls=cls.__name__):
                instance = cls()
                self.assertEqual(7, instance.value)
                self.assertEqual({'calls', 'value'}, set(instance.__dict__))
                restored = pickle.loads(pickle.dumps(instance))
                self.assertEqual(7, restored.value)
                self.assertEqual(1, restored.calls)
                self.assertEqual({}, cls.value._active_locks)

    def test_nonweakref_instance(self):
        for decorator in DECORATORS:
            with self.subTest(decorator=decorator.__name__):
                descriptor = decorator(lambda obj: 7)
                instance = NoWeakref()
                self.assertEqual(7, descriptor.__get__(instance, NoWeakref))
                self.assertEqual(7, descriptor.__get__(instance, NoWeakref))

    def test_ttl_assignment_invalidation_and_expiry_unchanged(self):
        class C:
            calls = 0

            @cp.threaded_cached_property_with_ttl(ttl=5)
            def value(self):
                self.calls += 1
                return self.calls

        instance = C()
        with patch.object(cp, 'time', return_value=100):
            self.assertEqual(1, instance.value)
        with patch.object(cp, 'time', return_value=104):
            instance.value = 9
        with patch.object(cp, 'time', return_value=108):
            self.assertEqual(9, instance.value)
        with patch.object(cp, 'time', return_value=110):
            self.assertEqual(2, instance.value)
            del instance.value
            self.assertEqual(3, instance.value)


if __name__ == '__main__':
    unittest.main()
