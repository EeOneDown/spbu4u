import unittest


def everything_ok():
    return True


class TestTest(unittest.TestCase):
    def test_everything_ok(self):
        self.assertTrue(everything_ok())
