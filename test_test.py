import requests
import time
import unittest
from functions import create_schedule_answer


def everything_ok():
    return True


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


class TestAllSchedules(unittest.TestCase):

    def test_answers_AGSM(self):
        alias = "AGSM"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_BIOL(self):
        alias = "BIOL"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_ORIS(self):
        alias = "ORIS"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_JOUR(self):
        alias = "JOUR"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_ARTS(self):
        alias = "ARTS"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_HIST(self):
        alias = "HIST"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_SC(self):
        alias = "SC"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_MATH(self):
        alias = "MATH"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_MEDI(self):
        alias = "MEDI"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_INTD(self):
        alias = "INTD"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_INTR(self):
        alias = "INTR"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_GSOM(self):
        alias = "GSOM"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_EARTH(self):
        alias = "EARTH"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_POLS(self):
        alias = "POLS"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_AMCP(self):
        alias = "AMCP"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_PSYC(self):
        alias = "PSYC"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_LIAS(self):
        alias = "LIAS"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_SOCL(self):
        alias = "SOCL"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_DENT(self):
        alias = "DENT"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_PHYS(self):
        alias = "PHYS"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_LETT(self):
        alias = "LETT"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_PHIL(self):
        alias = "PHIL"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_CHEM(self):
        alias = "CHEM"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_ECON(self):
        alias = "ECON"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_LAWS(self):
        alias = "LAWS"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_answers_LAWSPRIMARY(self):
        alias = "LAWSPRIMARY"
        for group_id in all_group_ids_for_alias(alias):
            print(group_id)
            for day_answer in get_group_week_schedules(alias, group_id):
                print("HERE_3")
                self.assertTrue(day_answer)

    def test_everything_ok(self):
        self.assertTrue(everything_ok())


if __name__ == '__main__':
    unittest.main()
