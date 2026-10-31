import unittest
from unittest.mock import patch

import cached_property


class TestCachedPropertyWithTTLAssignment(unittest.TestCase):
    cached_property_factory = cached_property.cached_property_with_ttl

    def test_assignment_starts_a_new_ttl(self):
        class Check:
            calls = 0

            @self.cached_property_factory(ttl=5)
            def value(self):
                self.calls += 1
                return self.calls

        check = Check()
        with patch("cached_property.time", return_value=100) as clock:
            self.assertEqual(check.value, 1)

            clock.return_value = 104
            check.value = "assigned"
            self.assertEqual(check.value, "assigned")
            self.assertEqual(check.calls, 1)

            # The original value has expired, but the assignment has not.
            clock.return_value = 108
            self.assertEqual(check.value, "assigned")
            self.assertEqual(check.calls, 1)

            # The assigned value expires according to its own TTL.
            clock.return_value = 110
            self.assertEqual(check.value, 2)
            self.assertEqual(check.value, 2)
            self.assertEqual(check.calls, 2)


class TestThreadedCachedPropertyWithTTLAssignment(TestCachedPropertyWithTTLAssignment):
    cached_property_factory = cached_property.threaded_cached_property_with_ttl
