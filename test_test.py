import unittest


def everything_ok():
    return "OK", True


class TestStringMethods(unittest.TestCase):
    def test_test(self):
        self.assertEqual(everything_ok(), ("OK", True))


if __name__ == '__main__':
    unittest.main()
