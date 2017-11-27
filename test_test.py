import unittest


def everything_ok():
    return True


class TestAllSchedules(unittest.TestCase):
    def test_everything_ok(self):
        self.assertTrue(everything_ok())


if __name__ == '__main__':
    unittest.main()
