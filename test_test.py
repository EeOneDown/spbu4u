# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest


def everything_ok():
    return True


class TestAllSchedules(unittest.TestCase):
    def test_everything_ok(self):
        self.assertTrue(everything_ok())


if __name__ == '__main__':
    unittest.main()
