import requests
import unittest
import re
from random import randint
from functions import create_schedule_answer


def everything_ok():
    return True


def get_all_aliases():
    aliases = []
    url = "https://timetable.spbu.ru/api/v1/study/divisions"
    data = requests.get(url).json()
    for alias in data:
        aliases.append(alias["Alias"])
    return aliases


def all_group_ids_for_alias(alias):
    group_ids = []
    url = "https://timetable.spbu.ru/api/v1/study/divisions/{}/" \
          "programs/levels".format(alias)
    study_programs_data = requests.get(url).json()
    for study_program in study_programs_data:
        for study_program_combination in study_program[
             "StudyProgramCombinations"]:
            for admission_year in study_program_combination["AdmissionYears"]:
                if not admission_year["IsEmpty"]:
                    study_program_id = admission_year["StudyProgramId"]
                    url = "https://timetable.spbu.ru/api/v1/progams/{}/" \
                          "groups".format(study_program_id)
                    groups_data = requests.get(url).json()
                    for group in groups_data["Groups"]:
                        group_ids.append(group["StudentGroupId"])
    print(alias, "Done")
    return group_ids


def get_group_week_schedules(group_id):
    answers = []
    url = "https://timetable.spbu.ru/api/v1/groups/{}/events".format(group_id)
    json_data = requests.get(url).json()
    for day_info in json_data["Days"]:
        answer = create_schedule_answer(day_info, full_place=True,
                                        personal=False)
        answers.append(answer)
    return answers


def get_all_schedules():
    all_answer = []
    for alias in get_all_aliases():
        for group_id in all_group_ids_for_alias(alias):
            all_answer.append(get_group_week_schedules(group_id))
    return all_answer


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
    '''
    def test_string(self):
        aliases = get_all_aliases()
        alias = aliases[randint(0, len(aliases) - 1)]
        for group_id in all_group_ids_for_alias(alias):
            for day_answer in get_group_week_schedules(group_id):
                print(alias, group_id, day_answer.split("\n")[0][2:])
                self.assertTrue(len(day_answer) <= 4096)
    '''
    '''
    def test_check_db_answers(self):
        for group_data in select_all_group_data():
            for day_data in group_data["Days"]:
                day_answer = create_schedule_answer(day_data, full_place=True,
                                                    personal=False)
                print(group_data["StudentGroupId"], len(day_answer))
                self.assertTrue(len(day_answer) <= 4096)
    '''
    def test_everything_ok(self):
        self.assertTrue(everything_ok())

    def test_re_full_names(self):
        for name in get_all_educators_names():
            print(name)
            self.assertTrue(re.fullmatch(r' *\w[^_#%&*+:?>/\\]*', name))

    def test_re_err_names(self):
        for name in ("Смирнов\В", "Смирнов&В. О.", "Смирнов_"):
            print(name)
            self.assertTrue(not re.fullmatch(r' *\w[^_#%&*+:?>/\\]*', name))


if __name__ == '__main__':
    unittest.main()
