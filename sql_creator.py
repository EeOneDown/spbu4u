import sqlite3


def create_sql(db_name):
    sql_con = sqlite3.connect(db_name)
    cursor = sql_con.cursor()

    # user choice
    cursor.execute("""CREATE TABLE user_choice
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
                            step TEXT DEFAULT 'handle_start' NOT NULL
                        )""")
    sql_con.commit()

    # group data
    cursor.execute("""CREATE TABLE groups_data
                        (
                            id INT PRIMARY KEY NOT NULL,
                            alias TEXT NOT NULL,
                            json_week_data TEXT,
                            interim_attestation TEXT
                        )""")
    sql_con.commit()

    # user data
    cursor.execute("""CREATE TABLE user_data
                        (
                            id INT PRIMARY KEY NOT NULL,
                            alias TEXT,
                            group_id INT NOT NULL,
                            full_place INT DEFAULT 1 NOT NULL,
                            sending INT DEFAULT 0 NOT NULL,
                            delete_skips INT DEFAULT 1 NOT NULL,
                            step TEXT DEFAULT 'main_menu' NOT NULL, 
                            rate INT DEFAULT 0 NOT NULL, 
                            home_station_code TEXT DEFAULT 'c2' NOT NULL, 
                            is_univer INT DEFAULT 1 NOT NULL,
                            CONSTRAINT user_data_groups_data_id_fk 
                              FOREIGN KEY (group_id) REFERENCES groups_data (id)
                        )""")
    sql_con.commit()

    # lessons
    cursor.execute("""CREATE TABLE lessons 
                        (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            name TEXT NOT NULL, 
                            type TEXT NOT NULL, 
                            day TEXT NOT NULL DEFAULT 'all', 
                            time TEXT NOT NULL DEFAULT 'all', 
                            UNIQUE (name, type, day, time)
                        )""")
    sql_con.commit()

    # skips
    cursor.execute("""CREATE TABLE skips
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
    cursor.execute("""CREATE TABLE user_groups
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
    
    cursor.close()
    sql_con.close()


if __name__ == '__main__':
    create_sql("Bot_db")
