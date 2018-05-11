# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from json import dumps

import spbu
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

import app.bot.functions as func
import app.bot.registration_functions as reg_func
from app.bot import bot
from app.bot.bots_constants import bot_name
from app.bot.constants import *
from app.bot.keyboards import *
from app.bot.yandex_timetable import get_yandex_timetable_data


@bot.message_handler(commands=["start"])
@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Сменить группу",
                     content_types=["text"])
def start_handler(message):
    answer = ""

    if bot_name != "Spbu4UBot" and message.chat.id not in ids.values():
        answer = "Это тестовый бот. Используйте @Spbu4UBot"
        bot.send_message(message.chat.id, answer)
        return

    if message.text == "/start":
        answer = "Приветствую!\n"
    elif message.text.split()[1].isdecimal():
        answer = "Приветствую!\nДобавляю тебя в группу..."
        bot_msg = bot.send_message(message.chat.id, answer)
        try:
            group_id = int(message.text.split()[1])
        except ValueError:
            answer = "Ошибка в id группы."
            bot.edit_message_text(answer, message.chat.id,
                                  bot_msg.message_id)
            message.text = "/start"
            start_handler(message)
            return

        try:
            res = spbu.get_group_events(group_id)
        except spbu.ApiException:
            answer = "Ошибка в id группы."
            bot.edit_message_text(answer, message.chat.id, bot_msg.message_id)
            message.text = "/start"
            start_handler(message)
            return

        group_title = res["StudentGroupDisplayName"][7:]
        func.add_new_user(message.chat.id, group_id, group_title)
        answer = "Готово!\nГруппа <b>{0}</b>".format(group_title)
        bot.edit_message_text(answer, message.chat.id, bot_msg.message_id,
                              parse_mode="HTML")
        answer = "Главное меню\n\n" \
                 "{0} - информация о боте\n" \
                 "{1} - оценить бота\n" \
                 "{2} - настройки\n" \
                 "{3} - электрички\n" \
                 "{4} - <b>редактор расписания</b>\n" \
                 "@Spbu4u_news - новости бота".format(emoji["info"],
                                                      emoji["star"],
                                                      emoji["settings"],
                                                      emoji["suburban"],
                                                      emoji["editor"])
        bot.send_message(chat_id=message.chat.id, text=answer,
                         reply_markup=main_keyboard,
                         parse_mode="HTML")
        return
    answer += "Загружаю список направлений..."
    bot_msg = bot.send_message(message.chat.id, answer)
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Укажи свое направление:"
    divisions = spbu.get_study_divisions()
    division_names = [division["Name"] for division in divisions]
    divisions_keyboard = ReplyKeyboardMarkup(True, False)
    for division_name in division_names:
        divisions_keyboard.row(division_name)
    divisions_keyboard.row("Поддержка", "Завершить")
    data = dumps(divisions)

    sql_con = func.get_connection()
    cursor = sql_con.cursor()
    cursor.execute("""DELETE FROM user_choice WHERE user_id = %s""",
                   (message.chat.id, ))
    sql_con.commit()
    cursor.execute("""INSERT INTO user_choice (user_id, divisions_json)
                      VALUES (%s, %s)""", (message.chat.id, data))
    sql_con.commit()
    cursor.close()
    sql_con.close()
    bot.edit_message_text(text="Готово!", chat_id=message.chat.id,
                          message_id=bot_msg.message_id)
    bot.send_message(message.chat.id, answer, reply_markup=divisions_keyboard)
    reg_func.set_next_step(message.chat.id, "select_division")


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Поддержка",
                     content_types=["text"])
def problem_text_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Если возникла проблема, то:\n" \
             "1. Возможно, информация по этому поводу есть в нашем канале" \
             " - @Spbu4u_news;\n" \
             "2. Ты всегда можешь связаться с " \
             "<a href='https://t.me/eeonedown'>разработчиком</a>."
    bot.send_message(message.chat.id, answer,
                     disable_web_page_preview=True,
                     parse_mode="HTML")


@bot.message_handler(commands=["exit"])
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Завершить",
                     content_types=["text"])
def exit_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    func.delete_user(message.chat.id, only_choice=False)
    remove_keyboard = ReplyKeyboardRemove(True)
    answer = "До встречи!"
    bot.send_message(message.chat.id, answer, reply_markup=remove_keyboard)


@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_division" and
                     mess.text != "/home" and mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_division_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_division(message)
    return


@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_study_level" and
                     mess.text != "/home" and mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_study_level_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_study_level(message)
    return


@bot.message_handler(
    func=lambda mess:
        reg_func.get_step(mess.chat.id) == "select_study_program_combination"
        and mess.text != "/home" and mess.text.capitalize() != "Назад",
    content_types=["text"])
def select_study_program_combination_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_study_program_combination(message)
    return


@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_admission_year"
                     and mess.text != "/home" and
                     mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_admission_year_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_admission_year(message)
    return


@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "select_student_group"
                     and mess.text != "/home" and
                     mess.text.capitalize() != "Назад",
                     content_types=["text"])
def select_student_group_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.select_student_group(message)
    return


@bot.message_handler(func=lambda mess:
                     reg_func.get_step(mess.chat.id) == "confirm_choice" and
                     mess.text != "/home" and mess.text.capitalize() != "Назад",
                     content_types=["text"])
def confirm_choice_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    reg_func.confirm_choice(message)
    return


@bot.message_handler(func=lambda mess: not func.is_user_exist(mess.chat.id),
                     content_types=["text"])
def not_exist_user_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Чтобы начать пользоваться сервисом, необходимо " \
             "зарегистрироваться.\nВоспользуйся коммандой /start"
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda mess: mess.text == emoji["info"],
                     content_types=["text"])
def help_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    inline_full_info_keyboard = InlineKeyboardMarkup()
    inline_full_info_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Благодарности"]])
    answer = briefly_info_answer
    bot.send_message(message.chat.id, answer,
                     parse_mode="HTML",
                     reply_markup=inline_full_info_keyboard,
                     disable_web_page_preview=True)


@bot.message_handler(commands=["home"])
@bot.message_handler(
    func=lambda mess:
        mess.text.capitalize() == "Назад" or
        mess.text == emoji["back"], content_types=["text"])
def home_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    func.delete_user(message.chat.id, only_choice=True)
    answer = "Главное меню"
    bot.send_message(message.chat.id, answer, reply_markup=main_keyboard)


@bot.message_handler(commands=["settings"])
@bot.message_handler(func=lambda mess: mess.text == emoji["settings"],
                     content_types=["text"])
def settings_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    func.delete_user(message.chat.id, only_choice=True)
    answer = "Настройки"
    bot.send_message(message.chat.id, answer, reply_markup=settings_keyboard)


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Расписание",
                     content_types=["text"])
def schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Меню расписания"
    bot.send_message(message.chat.id, answer, reply_markup=schedule_keyboard)


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Сегодня",
                     content_types=["text"])
def today_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    today_moscow_datetime = datetime.today() + server_timedelta
    today_moscow_date = today_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, today_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Завтра",
                     content_types=["text"])
def tomorrow_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    tomorrow_moscow_datetime = datetime.today() + server_timedelta + \
        timedelta(days=1)
    tomorrow_moscow_date = tomorrow_moscow_datetime.date()
    json_day = func.get_json_day_data(message.chat.id, tomorrow_moscow_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place, message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Неделя",
                     content_types=["text"])
def calendar_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Выбери день:"
    week_day_calendar = InlineKeyboardMarkup()
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in week_day_number.keys()])
    week_day_calendar.row(
        *[InlineKeyboardButton(text=name, callback_data=name) for
          name in ["Вся неделя"]])
    bot.send_message(message.chat.id, answer, reply_markup=week_day_calendar)


@bot.message_handler(func=lambda mess: mess.text == emoji["alarm_clock"],
                     content_types=["text"])
def sending_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь <b>подписаться</b> на рассылку расписания на " + \
             "следующий день или <b>отписаться</b> от неё.\n" + \
             "Рассылка производится в 21:00"
    sending_keyboard = InlineKeyboardMarkup(True)
    if func.is_sending_on(message.chat.id):
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Отписаться")
              for name in [emoji["cross_mark"] + " Отписаться"]])
    else:
        sending_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Подписаться")
              for name in [emoji["check_mark"] + " Подписаться"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=sending_keyboard)


@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Сессия",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text.capitalize() == "Допса",
                     content_types=["text"])
def attestation_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    month = func.get_available_months(message.chat.id)
    if len(month) == 0:
        bot.send_message(message.chat.id, "<i>Нет событий</i>",
                         parse_mode="HTML")
        return
    inline_keyboard = InlineKeyboardMarkup()
    for key in month.keys():
        inline_keyboard.row(
            *[InlineKeyboardButton(text=month[key], callback_data=str(key))]
        )
    if message.text == "Сессия":
        answer = "Выбери месяц:"
    else:
        answer = "Выбери месяц для Допсы:"
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard)


@bot.message_handler(func=lambda mess: mess.text == emoji["star"],
                     content_types=["text"])
def rate_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Оцените качество сервиса:"
    user_rate = func.get_user_rate(message.chat.id)
    rate_keyboard = InlineKeyboardMarkup(row_width=5)
    rate_keyboard.add(*[InlineKeyboardButton(
        text=emoji["star2"] if user_rate < count_of_stars else emoji["star"],
        callback_data=str(count_of_stars))
        for count_of_stars in (1, 2, 3, 4, 5)])
    rate_keyboard.add(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Связь", "Статистика"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=rate_keyboard)


@bot.message_handler(func=lambda mess: mess.text == emoji["suburban"],
                     content_types=["text"])
def suburban_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    answer = "Меню расписания электричек\n\n" \
             "Данные предоставлены сервисом " \
             "<a href = 'http://rasp.yandex.ru/'>Яндекс.Расписания</a>"
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=suburban_keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)


@bot.message_handler(func=lambda mess: mess.text.title() == "В Универ",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text.title() == "Домой",
                     content_types=["text"])
def to_university_handler(message):
    bot.send_chat_action(message.chat.id, "typing")

    if message.text.title() == "В Универ":
        from_station = func.get_station_code(message.chat.id, is_home=True)
        to_station = func.get_station_code(message.chat.id, is_home=False)
    else:
        from_station = func.get_station_code(message.chat.id, is_home=False)
        to_station = func.get_station_code(message.chat.id, is_home=True)

    server_datetime = datetime.today() + server_timedelta
    data = get_yandex_timetable_data(from_station, to_station, server_datetime)
    answer = data["answer"]

    update_keyboard = InlineKeyboardMarkup(True)
    if data["is_OK"]:
        if data["is_tomorrow"]:
            bot.send_message(message.chat.id, emoji["warning"] +
                             " На сегодня нет электричек")
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Все на завтра"]])
        else:
            update_keyboard.row(*[InlineKeyboardButton(
                text=name, callback_data=name)
                for name in ["Оставшиеся", "Обновить"]])

    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=update_keyboard,
                     parse_mode='HTML',
                     disable_web_page_preview=True)


@bot.message_handler(func=lambda mess: mess.text.title() == "Маршрут",
                     content_types=["text"])
def own_trail_handler(message):
    answer = "Выбери начальную станцию:"
    start_station_keyboard = InlineKeyboardMarkup(True)
    for station_title in all_stations.keys():
        start_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in [station_title]])
    start_station_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Домой", "В Универ"]])
    bot.send_message(message.chat.id, answer,
                     reply_markup=start_station_keyboard)


@bot.message_handler(func=lambda mess: mess.text.title() == "Персонализация",
                     content_types=["text"])
def personalisation_handler(message):
    home_station = func.get_station_code(message.chat.id, is_home=True)
    univer_station = func.get_station_code(message.chat.id, is_home=False)

    home_station_title = func.get_key_by_value(all_stations, home_station)
    univer_station_title = func.get_key_by_value(all_stations, univer_station)

    answer = "Здесь ты можешь настроить <b>домашнюю</b> и " \
             "<b>Университетскую</b> станции для команд <i>Домой</i> и " \
             "<i>В Универ</i>\n\n" \
             "<b>Домашняя:</b> {0}\n<b>Университетская:</b> {1}".format(
                                    home_station_title, univer_station_title)

    inline_keyboard = InlineKeyboardMarkup(True)
    inline_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Домашняя"]])
    inline_keyboard.row(*[InlineKeyboardButton(
            text=name, callback_data=name) for name in ["Университетская"]])
    bot.send_message(message.chat.id, answer,
                     reply_markup=inline_keyboard, parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text.title() == "Редактор",
                     content_types=["text"])
@bot.message_handler(func=lambda mess: mess.text == emoji["editor"],
                     content_types=["text"])
def schedule_editor_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Редактор расписания"
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=schedule_editor_keyboard,
                     parse_mode='HTML')


@bot.message_handler(func=lambda mess: mess.text.title() == "Адрес",
                     content_types=["text"])
def place_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь выбрать отображаемый формат адреса\nСейчас: "
    place_keyboard = InlineKeyboardMarkup(True)
    if func.is_full_place(message.chat.id):
        answer += "<b>Полностью</b>"
        place_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Аудитория")
              for name in ["Только аудитория"]])
    else:
        answer += "<b>Только аудитория</b>"
        place_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data="Полностью")
              for name in ["Полностью"]])
    bot.send_message(message.chat.id, answer, parse_mode="HTML",
                     reply_markup=place_keyboard)


@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Выбрать",
                     content_types=["text"])
def choose_educator_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь выбрать для отображения занятие или " \
             "преподавателя:"
    inline_keyboard = InlineKeyboardMarkup(True)
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподавателя", "Занятие"]])
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard)


@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Скрыть",
                     content_types=["text"])
def hide_lesson_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Здесь ты можешь скрыть любое занятие\n" \
             "Выбери день, когда есть это занятие:"
    json_week_data = func.get_json_week_data(message.chat.id)
    days = json_week_data["Days"]
    days_keyboard = InlineKeyboardMarkup(True)
    for day in days:
        days_keyboard.row(
            *[InlineKeyboardButton(text=name, callback_data=name)
              for name in [day["DayString"].split(", ")[0].capitalize()]])
    days_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Отмена"]])
    bot.send_message(message.chat.id, answer, reply_markup=days_keyboard)


@bot.message_handler(func=lambda mess: mess.text.title() == "Вернуть",
                     content_types=["text"])
def chose_to_return(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Выбери, что ты хочешь вернуть:"
    inline_keyboard = InlineKeyboardMarkup(True)
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Преподавателей", "Занятия"]])
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Полный сброс"]])
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard)


@bot.message_handler(
    func=lambda mess:
        mess.reply_to_message is not None and
        mess.reply_to_message.from_user.username == bot_name and
        mess.reply_to_message.text == "Напиши мне что-нибудь:",
    content_types=["text"])
def users_callback_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    bot.forward_message(ids["my"], message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "Записал", reply_markup=main_keyboard,
                     reply_to_message_id=message.message_id)


@bot.message_handler(func=lambda mess:
                     mess.text == emoji["arrows_counterclockwise"],
                     content_types=["text"])
def group_templates_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = ""
    groups = func.get_templates(message.chat.id)
    group_title = func.get_current_group(message.chat.id)[1]
    answer += "Текущая группа: <b>{0}</b>\n".format(group_title)
    last_row = ["Отмена", "Сохранить"]
    inline_keyboard = InlineKeyboardMarkup(row_width=2)
    if len(groups) == 0:
        answer += "Нет шаблонов групп, но ты можешь сохранить текущую\n"
    else:
        answer += "Выбери группу:"
        inline_keyboard.add(
            *[InlineKeyboardButton(
                text=name, callback_data=str(groups[name]))
                for name in groups.keys()]
        )
        if group_title in groups.keys():
            last_row = ["Отмена", "Удалить"]
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
            for name in last_row]
    )
    inline_keyboard.row(
        *[InlineKeyboardButton(text=name, callback_data=name)
          for name in ["Сменить группу"]]
    )
    bot.send_message(message.chat.id, answer, reply_markup=inline_keyboard,
                     parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text == emoji["bust_in_silhouette"],
                     content_types=["text"])
def educator_schedule_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
    markup = ForceReply(False)
    bot.send_message(message.chat.id, answer, reply_markup=markup,
                     parse_mode="HTML")


@bot.message_handler(
    func=lambda mess:
        mess.reply_to_message is not None and
        mess.reply_to_message.from_user.username == bot_name and
        "Введи Фамилию преподавателя:" in mess.reply_to_message.text,
    content_types=["text"])
def write_educator_name_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = ""
    name = message.text.strip(". ")
    if not func.is_correct_educator_name(name):
        answer = "Недопустимые символы"
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
        return

    try:
        educators_data = spbu.search_educator(name)
    except spbu.ApiException:
        answer = "Во время выполнения запроса произошла ошибка."
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
        return

    if not educators_data["Educators"]:
        answer = "Никого не найдено"
        bot.send_message(message.chat.id, answer,
                         reply_markup=schedule_keyboard)
    elif len(educators_data["Educators"]) > 200:
        answer = "Слишком много преподавателей\n" \
                 "Пожалуйста, <b>уточни</b>"
        bot.send_message(message.chat.id, answer, parse_mode="HTML")
        answer = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
        markup = ForceReply(False)
        bot.send_message(message.chat.id, answer, reply_markup=markup,
                         parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "Готово!",
                         reply_markup=schedule_keyboard)

        educators_keyboard = InlineKeyboardMarkup(row_width=2)
        educators_keyboard.add(
            *[InlineKeyboardButton(text=educator["DisplayName"],
                                   callback_data=str(educator["Id"]))
              for educator in educators_data["Educators"]])
        educators_keyboard.row(InlineKeyboardButton(
            text="Отмена", callback_data="Отмена"))
        answer = "{0} Найденные преподаватели:\n\n".format(
            emoji["mag_right"]) + answer
        bot.send_message(message.chat.id, answer,
                         reply_markup=educators_keyboard, parse_mode="HTML")


@bot.message_handler(func=lambda mess: mess.text.title() == "Сейчас",
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.capitalize() == "Что сейчас?",
                     content_types=["text"])
def now_lesson_handler(message):
    answer = "Наверно, какая-то пара #пасхалочка"
    func.send_long_message(bot, answer, message.chat.id)


@bot.message_handler(func=lambda mess: func.text_to_date(mess.text.lower()),
                     content_types=["text"])
def schedule_for_day(message):
    bot.send_chat_action(message.chat.id, "typing")
    day = func.text_to_date(message.text.lower())
    json_week = func.get_json_week_data(message.chat.id, for_day=day)
    json_day = func.get_json_day_data(message.chat.id, day_date=day,
                                      json_week_data=json_week)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         user_id=message.chat.id,
                                         personal=True)
    func.send_long_message(bot, answer, message.chat.id)


@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.keys(),
                     content_types=["text"])
@bot.message_handler(func=lambda mess:
                     mess.text.title() in week_day_titles.values(),
                     content_types=["text"])
def schedule_for_weekday(message):
    bot.send_chat_action(message.chat.id, "typing")
    message.text = message.text.title()
    if message.text in week_day_titles.values():
        week_day = message.text
    else:
        week_day = week_day_titles[message.text]

    day_date = func.get_day_date_by_weekday_title(week_day)
    json_day = func.get_json_day_data(message.chat.id, day_date)
    full_place = func.is_full_place(message.chat.id)
    answer = func.create_schedule_answer(json_day, full_place,
                                         message.chat.id)
    func.send_long_message(bot, answer, message.chat.id)


@bot.message_handler(func=lambda mess: True, content_types=["text"])
def other_text_handler(message):
    bot.send_chat_action(message.chat.id, "typing")
    answer = "Не понимаю"
    func.send_long_message(bot, answer, message.chat.id)
