# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from app import constants as const, new_functions as nf
from datetime import date


def is_usual_year(y):
    return y % 4 != 0 or (y % 100 == 0 and y % 400 != 0)


class TestNewFunctions(unittest.TestCase):
    def test_leap_years(self):
        for y in range(1880, 2073):
            if y in [1880, 1884, 1888, 1892, 1896, 1904, 1908, 1912, 1916,
                     1920, 1924, 1928, 1932, 1936, 1940, 1944, 1948, 1952,
                     1956, 1960, 1964, 1968, 1972, 1976, 1980, 1984, 1988,
                     1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024,
                     2028, 2032, 2036, 2040, 2044, 2048, 2052, 2056, 2060,
                     2064, 2068, 2072]:
                self.assertFalse(is_usual_year(y))
            else:
                self.assertTrue(is_usual_year(y))

    def test_text_to_date_d(self, text_t=None, m=None, y=None, s=None):
        m_30 = [4, 6, 9, 11, "апреля", "июня", "сентября", "ноября"]

        if not m:
            m = date.today().month
        if not y:
            y = date.today().year
        if not text_t:
            text_t = "{0}"

        for d in range(1, 32):
            if m in (2, "февраля") and d > 28:
                if d == 29 and not is_usual_year(y):
                    self.assertTrue(nf.text_to_date(
                        text_t.format(
                            str(d), str(m), str(y), s
                        )
                    ))
                else:
                    self.assertFalse(nf.text_to_date(
                        text_t.format(
                            str(d), str(m), str(y), s
                        )
                    ))
            elif m in m_30 and d > 30:
                self.assertFalse(nf.text_to_date(
                    text_t.format(
                        str(d), str(m), str(y), s
                    )
                ))
            else:
                self.assertTrue(nf.text_to_date(
                    text_t.format(
                        str(d), str(m), str(y), s
                    )
                ))

    def test_text_to_date_dm(self, text_t=None, y=None, s=None):
        if not text_t:
            text_t = "{0}{3}{1:0>2}"
        if not y:
            y = None
        if not s:
            ss = [" ", "."]
        else:
            ss = [s]

        for c in ss:
            for m in range(1, 13):
                self.test_text_to_date_d(text_t, m, y, c)
                self.test_text_to_date_d(
                    text_t, nf.get_key_by_value(const.months, m), y, c
                )

    def test_text_to_date_dmy(self):
        text_t = "{0}{3}{1:0>2}{3}{2}"
        for s in [" ", "."]:
            for y in range(2018, 2100):
                self.test_text_to_date_dm(text_t, y, s)


if __name__ == '__main__':
    unittest.main()
