import sys

sys.path.append('../')

import unittest
from datetime import date, datetime, timedelta

from app import constants as const, new_functions as nf


def is_usual_year(y):
    return y % 4 != 0 or (y % 100 == 0 and y % 400 != 0)


class TestNewFunctions(unittest.TestCase):
    def test_leap_years(self):
        for y in range(2018, 2073):
            if y in [2020, 2024, 2028, 2032, 2036, 2040, 2044,
                     2048, 2052, 2056, 2060, 2064, 2068, 2072]:
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

    def test_text_to_interval(self):
        self.assertEqual(
            nf.text_to_interval("2 05 2018 - 3 10 2018"),
            (date(2018, 5, 2), date(2018, 10, 3))
        )
        self.assertEqual(
            nf.text_to_interval("2 05 - 3 10"),
            (date(date.today().year, 5, 2), date(date.today().year, 10, 3))
        )
        self.assertEqual(
            nf.text_to_interval("2 - 10"),
            (date(date.today().year, date.today().month, 2),
             date(date.today().year, date.today().month, 10))
        )
        self.assertFalse(
            nf.text_to_interval("10 - 2"),
        )
        self.assertFalse(
            nf.text_to_interval("3.10 - 2.05")
        )
        self.assertFalse(
            nf.text_to_interval("3.10.2019 - 2.05.2018")
        )

    def test_get_term_dates(self):
        terms = (
            (date(2018, 8, 1), date(2019, 2, 1)),
            (date(2019, 2, 1), date(2019, 8, 1)),
            (date(2019, 8, 1), date(2020, 2, 1))
        )
        self.assertTrue(nf.get_term_dates() in terms)

    def test_datetime_from_string(self):
        self.assertEqual(
            nf.datetime_from_string("2018-09-03T09:30:00"),
            datetime(2018, 9, 3, 9, 30, 0)
        )
        self.assertEqual(
            nf.datetime_from_string("2018-09-07T15:15:00Z"),
            datetime(2018, 9, 7, 15, 15, 0)
        )
        self.assertEqual(
            nf.datetime_from_string("2017-03-28T06:00:00+03:00"),
            datetime(2017, 3, 28, 6, 0, 0)
        )

    def test_get_work_monday(self):
        mondays = [date(2018, 9, 3)]
        for i in range(500):
            mondays.append(mondays[i] + timedelta(days=7))
        self.assertTrue(nf.get_work_monday() in mondays)

    def test_get_date_by_weekday_title(self):
        mondays = [date(2018, 9, 3)]
        tuesdays = [date(2018, 9, 4)]
        wednesdays = [date(2018, 9, 5)]
        thursdays = [date(2018, 9, 6)]
        fridays = [date(2018, 9, 7)]
        saturdays = [date(2018, 9, 8)]
        for i in range(500):
            mondays.append(mondays[i] + timedelta(days=7))
            tuesdays.append(tuesdays[i] + timedelta(days=7))
            wednesdays.append(wednesdays[i] + timedelta(days=7))
            thursdays.append(thursdays[i] + timedelta(days=7))
            fridays.append(fridays[i] + timedelta(days=7))
            saturdays.append(saturdays[i] + timedelta(days=7))
        self.assertTrue(nf.get_date_by_weekday_title("Пн") in mondays)
        self.assertTrue(nf.get_date_by_weekday_title("Вт") in tuesdays)
        self.assertTrue(nf.get_date_by_weekday_title("Ср") in wednesdays)
        self.assertTrue(nf.get_date_by_weekday_title("Чт") in thursdays)
        self.assertTrue(nf.get_date_by_weekday_title("Пт") in fridays)
        self.assertTrue(nf.get_date_by_weekday_title("Сб") in saturdays)

    def test_datetime_to_string(self):
        self.assertEqual(
            nf.datetime_to_string(date(2018, 1, 1)),
            "1 января 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 2, 1)),
            "1 февраля 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 3, 1)),
            "1 марта 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 4, 1)),
            "1 апреля 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2022, 5, 15)),
            "15 мая 2022"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 6, 1)),
            "1 июня 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 7, 1)),
            "1 июля 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 8, 1)),
            "1 августа 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 9, 1)),
            "1 сентября 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 10, 1)),
            "1 октября 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 11, 1)),
            "1 ноября 2018"
        )
        self.assertEqual(
            nf.datetime_to_string(date(2018, 12, 1)),
            "1 декабря 2018"
        )

    def test_get_hours_minutes_by_seconds(self):
        self.assertEqual(
            nf.get_hours_minutes_by_seconds(600),
            (0, 10)
        )
        self.assertEqual(
            nf.get_hours_minutes_by_seconds(-600),
            (-1, 50)
        )
        self.assertEqual(
            nf.get_hours_minutes_by_seconds(0),
            (0, 0)
        )


if __name__ == '__main__':
    unittest.main()
