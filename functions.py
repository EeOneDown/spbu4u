# -*- coding: utf-8 -*-
import sqlite3


def set_next_step(user_id, next_step):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""UPDATE user_choice
                      SET step = ? 
                      WHERE user_id = ?""",
                   (next_step, user_id))
    sql_con.commit()
    cursor.close()
    sql_con.close()


def get_step(user_id):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""SELECT  step
                      FROM user_choice
                      WHERE user_id = ?""", (user_id, ))
    step = cursor.fetchone()
    cursor.close()
    sql_con.close()
    if step is None:
        return None
    else:
        return step[0]


def delete_user(user_id, only_choice=False):
    sql_con = sqlite3.connect("Bot_db")
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_choice WHERE user_id = ?""",
                   (user_id,))
    sql_con.commit()
    if not only_choice:
        cursor.execute("""DELETE FROM user_data WHERE id = ?""",
                       (user_id,))
        sql_con.commit()
        cursor.execute("""DELETE FROM user_groups WHERE user_id = ?""",
                       (user_id,))
        sql_con.commit()
    cursor.close()
    sql_con.close()
