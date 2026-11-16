"""Regression tests for imported cached-property doctest discovery."""
import asyncio
import doctest
import inspect
import sys
import types
import unittest

from cached_property import cached_property


class DoctestDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.module = types.ModuleType("cached_property_doctest_consumer")
        sys.modules[self.module.__name__] = self.module
        self.addCleanup(sys.modules.pop, self.module.__name__)
        self.module.cached_property = cached_property
        exec('''class Example:
    @cached_property
    def value(self):
        """A cached value.

        >>> Example().value
        42
        """
        return 42

    @property
    def control(self):
        """An ordinary property.

        >>> Example().control
        7
        """
        return 7
''', self.module.__dict__)

    def test_imported_descriptor_examples_are_found_and_run(self):
        tests = doctest.DocTestFinder().find(self.module)
        names = {test.name for test in tests if test.examples}
        self.assertEqual(names, {
            "cached_property_doctest_consumer.Example.value",
            "cached_property_doctest_consumer.Example.control",
        })
        runner = doctest.DocTestRunner()
        for test in tests:
            runner.run(test)
        self.assertEqual(runner.summarize(), (0, 2))

    def test_imported_class_is_not_collected_in_unrelated_module(self):
        other = types.ModuleType("cached_property_unrelated")
        other.Example = self.module.Example
        self.assertEqual(doctest.DocTestFinder().find(other), [])

    def test_cache_assignment_and_delete_preserve_non_data_semantics(self):
        class Counter:
            __hash__ = None
            calls = 0

            @cached_property
            def value(self):
                self.calls += 1
                return self.calls

        descriptor = Counter.value
        self.assertFalse(inspect.isdatadescriptor(descriptor))
        one, two = Counter(), Counter()
        self.assertEqual((one.value, one.value, two.value), (1, 1, 1))
        one.value = 99
        self.assertEqual(one.value, 99)
        del one.value
        self.assertEqual(one.value, 2)
        self.assertEqual(two.value, 1)

    def test_async_property_still_caches_same_future(self):
        class Example:
            calls = 0

            @cached_property
            async def value(self):
                self.calls += 1
                return 42

        async def check():
            example = Example()
            first = example.value
            self.assertIs(first, example.value)
            self.assertEqual(await first, 42)
            self.assertEqual(await example.value, 42)
            self.assertEqual(example.calls, 1)

        asyncio.run(check())


if __name__ == "__main__":
    unittest.main()
