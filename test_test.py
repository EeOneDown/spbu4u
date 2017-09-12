import requests
import time
from random import randint
import unittest
from functions import create_schedule_answer


def everything_ok():
    return "OK", True


def get_all_aliases():
    aliases = []
    url = "https://timetable.spbu.ru/api/v1/divisions"
    data = requests.get(url).json()
    for alias in data:
        aliases.append(alias["Alias"])
    return aliases


def all_group_ids_for_alias(alias):
    group_ids = []
    url = "https://timetable.spbu.ru/api/v1/{}/studyprograms".format(alias)
    study_programs_data = requests.get(url).json()
    for study_program in study_programs_data:
        for study_program_combination in study_program[
             "StudyProgramCombinations"]:
            for admission_year in study_program_combination["AdmissionYears"]:
                if not admission_year["IsEmpty"]:
                    study_program_id = admission_year["StudyProgramId"]
                    url = "https://timetable.spbu.ru/api/v1/{}/studyprogram" \
                          "/{}/studentgroups".format(alias, study_program_id)
                    groups_data = requests.get(url).json()
                    for group in groups_data:
                        group_ids.append(group["StudentGroupId"])
                time.sleep(2)
    print(alias, "Done")
    return group_ids


def get_group_week_schedules(alias, group_id):
    answers = []
    url = "https://timetable.spbu.ru/api/v1/{}/studentgroup/{}/" \
          "events".format(alias, group_id)
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
            all_answer.append(get_group_week_schedules(alias, group_id))
    return all_answer


def print_all():
    for group_schedules in get_all_schedules():
        for schedule in group_schedules:
            print(schedule)
        print("===============================\n")
    return True


class TestAllSchedules(unittest.TestCase):

    def test_string(self):
        aliases = get_all_aliases()
        alias = aliases[randint(0, len(aliases))]
        print(alias)
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)


if __name__ == '__main__':
    unittest.main()
