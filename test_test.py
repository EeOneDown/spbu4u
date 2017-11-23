import unittest

import requests

from constants import emoji
from functions import is_correct_educator_name


def everything_ok():
    return True


def get_all_educators_names():
    url = "https://timetable.spbu.ru/api/v1/educators/search/_"
    req = requests.get(url).json()
    names = []
    for educator in req["Educators"]:
        names.append(educator["FullName"])
        comb = educator["FullName"].split()[0]
        names.append(comb)
        for word in educator["FullName"].split()[1:]:
            comb += " " + word
            names.append(comb)
        names.append(educator["DisplayName"])
        comb = educator["DisplayName"].split()[0]
        names.append(comb)
        for word in educator["DisplayName"].split()[1:]:
            comb += " " + word
            names.append(comb)
    return names


class TestAllSchedules(unittest.TestCase):
    def test_everything_ok(self):
        self.assertTrue(everything_ok())

    def test_correct_educators(self):
        for name in get_all_educators_names():
            print(name)
            self.assertTrue(is_correct_educator_name(name.strip()))

    def test_wrong_educator_names(self):
        for name in ("Smirnov ^<", "\" \\", "!№;%:?*()+=_", emoji["warning"]):
            print(name)
            self.assertTrue(not is_correct_educator_name(name.strip()))


if __name__ == '__main__':
    unittest.main()
