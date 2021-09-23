import unittest
from datetime import timedelta
from datetime import datetime

from scripts.main import within_allocated_time, clamp


class TestMaxTime(unittest.TestCase):

    def test_under_time(self):
        now = datetime.now()
        max_time = timedelta(seconds = 60)
        self.assertTrue(within_allocated_time(now + max_time))

    def test_over_time(self):
        now = datetime.now()
        max_time = timedelta(seconds = 60)
        self.assertFalse(within_allocated_time(now - max_time))

class TestClamp(unittest.TestCase):

    def test_within_clamp(self):
        self.assertEqual(15, clamp(15, 0, 30))

    def test_less_than_clamp(self):
        self.assertEqual(0, clamp(-10, 0, 30))

    def test_greater_than_clamp(self):
        self.assertEqual(30, clamp(50, 0, 30))

    def test_switched_order_clamp(self):
        self.assertEqual(5, clamp(5, 10, 0))


if __name__ == '__main__':
    unittest.main()
