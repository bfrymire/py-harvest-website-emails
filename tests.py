import unittest
from datetime import timedelta
from datetime import datetime

from scripts.main import within_allocated_time


class TestMaxTime(unittest.TestCase):

    def test_under_time(self):
        now = datetime.now()
        max_time = timedelta(seconds = 60)
        self.assertTrue(within_allocated_time(now + max_time))

    def test_over_time(self):
        now = datetime.now()
        max_time = timedelta(seconds = 60)
        self.assertFalse(within_allocated_time(now - max_time))



if __name__ == '__main__':
    unittest.main()
