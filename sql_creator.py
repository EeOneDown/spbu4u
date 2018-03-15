# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functions import get_connection


def create_sql():
    sql_con = get_connection()
    cursor = sql_con.cursor()

    # user choice
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_choice
                        (
                            user_id INT PRIMARY KEY,
                            divisions_json TEXT,
                            alias TEXT,
                            division_name TEXT,
                            study_programs_json TEXT,
                            study_level_name TEXT,
                            study_program_combination_name TEXT,
                            admission_year_name TEXT,
                            student_groups_json TEXT,
                            student_group_name TEXT,
                            student_group_id INT, 
                            step VARCHAR(40) DEFAULT 'handle_start' NOT NULL
                        )""")
    sql_con.commit()

    # group data
    cursor.execute("""CREATE TABLE IF NOT EXISTS groups_data
                        (
                            id INT PRIMARY KEY NOT NULL,
                            title TEXT NOT NULL
                        )""")
    sql_con.commit()

    # user data
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_data
                        (
                            id INT PRIMARY KEY NOT NULL,
                            group_id INT NOT NULL,
                            is_teacher INT DEFAULT 0 NOT NULL,
                            full_place INT DEFAULT 1 NOT NULL,
                            sending INT DEFAULT 0 NOT NULL,
                            rate INT DEFAULT 0 NOT NULL, 
                            home_station_code VARCHAR(8) DEFAULT 'c2' NOT NULL, 
                            univer_station_code VARCHAR(8) 
                                              DEFAULT 's9603770' NOT NULL,
                            CONSTRAINT user_data_groups_data_id_fk 
                              FOREIGN KEY (group_id) REFERENCES groups_data (id)
                        )""")
    sql_con.commit()

    # lessons
    cursor.execute("""CREATE TABLE IF NOT EXISTS lessons 
                        (
                            id INTEGER PRIMARY KEY AUTO_INCREMENT, 
                            name VARCHAR(500) NOT NULL, 
                            types VARCHAR(250) NOT NULL, 
                            day VARCHAR(11) NOT NULL DEFAULT 'all', 
                            time VARCHAR(11) NOT NULL DEFAULT 'all',
                            educators VARCHAR(200) NOT NULL DEFAULT 'all', 
                            UNIQUE (name, types, day, time, educators)
                        )""")
    sql_con.commit()

    # skips
    cursor.execute("""CREATE TABLE IF NOT EXISTS skips
                        (
                            lesson_id INT NOT NULL,
                            user_id INT NOT NULL,
                            CONSTRAINT skips_lesson_id_user_id_pk 
                              PRIMARY KEY (lesson_id, user_id),
                            CONSTRAINT skips_user_data_id_fk 
                              FOREIGN KEY (user_id) REFERENCES user_data (id),
                            CONSTRAINT skips_lessons_id_fk 
                              FOREIGN KEY (lesson_id) REFERENCES lessons (id)
                        )""")
    sql_con.commit()

    # user groups
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_groups
                        (
                            group_id INT NOT NULL,
                            user_id INT NOT NULL,
                            CONSTRAINT user_groups_group_id_user_id_pk 
                              PRIMARY KEY (group_id, user_id),
                            CONSTRAINT user_groups_user_data_id_fk 
                              FOREIGN KEY (user_id) REFERENCES user_data (id),
                            CONSTRAINT user_groups_groups_data_id_fk 
                              FOREIGN KEY (group_id) REFERENCES groups_data (id)
                        )""")
    sql_con.commit()

    # user educators
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_educators
                            (
                                user_id INT NOT NULL,
                                lesson_id INT NOT NULL,
                                CONSTRAINT user_educators_user_id_lesson_id_pk 
                                  PRIMARY KEY  (user_id, lesson_id),
                                CONSTRAINT user_educators_user_data_id_fk 
                                  FOREIGN KEY (user_id) 
                                    REFERENCES user_data (id),
                                CONSTRAINT user_educators_lessons_id_fk 
                                  FOREIGN KEY (lesson_id) 
                                    REFERENCES lessons (id)
                            )""")
    sql_con.commit()

    # user_lessons
    cursor.execute("""CREATE TABLE IF NOT EXISTS user_lessons
                                (
                                    user_id INT NOT NULL,
                                    lesson_id INT NOT NULL,
                                    CONSTRAINT user_lessons_user_id_lesson_id_pk 
                                      PRIMARY KEY  (user_id, lesson_id),
                                    CONSTRAINT user_lessons_user_data_id_fk 
                                      FOREIGN KEY (user_id) 
                                        REFERENCES user_data (id),
                                    CONSTRAINT user_lessons_lessons_id_fk 
                                      FOREIGN KEY (lesson_id) 
                                        REFERENCES lessons (id)
                                )""")
    sql_con.commit()

    cursor.close()
    sql_con.close()


if __name__ == '__main__':
    create_sql()
