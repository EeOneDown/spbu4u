# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hmac
import re
from collections import OrderedDict
from datetime import timedelta
from hashlib import sha256

from config import Config

sha_string = hmac.new(
    bytearray(Config.SECRET_KEY, "utf-8"),
    bytearray(Config.OTHER_SECRET_KEY, "utf-8"),
    sha256
).hexdigest()

ids = {
    "my": 200466757,
    "ks": 71591548
}

webhook_host = ""
webhook_port = 443
webhook_url_base = "https://{0}:{1}/tg".format(webhook_host, webhook_port)
webhook_url_path = "/{0}/".format(sha_string)

max_inline_button_text_len = 32
max_answers_count = 10

# TODO remove
server_timedelta = timedelta(hours=0)

urls = {
    "ya_search": "https://api.rasp.yandex.net/v3.0/search/"
}

emoji = {"info": "\U00002139", "star": "\U00002B50",
         "settings": "\U00002699", "suburban": "\U0001F689",
         "editor": "\U0001F4DD", "alarm_clock": "\U000023F0",
         "calendar": "\U0001F4C5", "sleep": "\U0001F634",
         "clock": "\U0001F552", "cross_mark": "\U0000274C",
         "check_mark": "\U00002705", "mailbox_off": "\U0001F4EA",
         "mailbox_on": "\U0001F4EB", "door": "\U0001F6AA",
         "school": "\U0001F3EB", "disappointed": "\U0001F61E",
         "cold_sweat": "\U0001F613", "halo": "\U0001F607",
         "smile": "\U0001F604", "bullet": "\U00002022",
         "horns": "\U0001F608", "orange_diamond": "\U0001F538",
         "blue_diamond": "\U0001F539", "runner": "\U0001F3C3",
         "arrow_up": "\U00002B06", "warning": "\U000026A0",
         "arrows_counterclockwise": "\U0001F504",
         "bust_in_silhouette": "\U0001F464", "back": "\U0001F519",
         "mag_right": "\U0001F50E", "arrow_backward": "\U000025C0",
         "arrow_forward": "\U000025B6", "star2": "\U00002728",
         "new": "\U0001F195", "prev_block": "\U00002B05",
         "next_block": "\U000027A1", "Отмена": "Отмена",
         "heavy_check_mark": "\U00002705", "ruble_sign": "\U000020BD",
         "train": "\U0001F683", "express": "\U0001F684",
         "en_dash": "\U00002013", "couch_and_lamp": "\U0001F6CB",
         "books": "\U0001F4DA"}

week_day_number = OrderedDict([
    ("Пн", 1), ("Вт", 2), ("Ср", 3), ("Чт", 4), ("Пт", 5), ("Сб", 6)
])

week_day_titles = OrderedDict([
    ("Понедельник", "Пн"), ("Вторник", "Вт"), ("Среда", "Ср"),
    ("Четверг", "Чт"), ("Пятница", "Пт"), ("Суббота", "Сб")
])

subject_short_types = OrderedDict([
    ("лекция", "Л"), ("практическое занятие", "ПР"), ("сам. работа", "СР"),
    ("семинар", "С"), ("урок", "У"), ("лабораторная работа", "ЛР"),
    ("контрольная работа", "КР"), ("показ работ", "ПОКАЗ РАБОТ"),
    ("текущий контроль", "ТК"), ("зачёт", "ЗАЧЁТ"),
    ("зачёт (пересдача)", "ЗАЧЁТ (ПЕР.)"), ("консультация групповая", "КОНС"),
    ("экзамен", "ЭКЗАМЕН"), ("экзамен (пересдача)", "ЭКЗАМЕН (ПЕР.)")
])

all_stations = OrderedDict([
    ("Санкт-Петербург", "c2"), ("Броневая", "s9603500"),
    ("Ленинский Проспект", "s9603435"), ("Дачное", "s9603596"),
    ("Ульянка", "s9603532"), ("Лигово", "s9603837"),
    ("Сосновая Поляна", "s9603431"), ("Сергиево (Володарская)", "s9603567"),
    ("Стрельна", "s9603542"), ("Красные Зори", "s9603483"),
    ("Новый Петергоф", "s9603887"), ("Старый Петергоф", "s9603547"),
    ("Университетская (Университет)", "s9603770"), ("Мартышкино", "s9603619"),
    ("Ораниенбаум-1", "s9603138"), ("Лебяжье", "s9602688"),
    ("Калище", "s9602687")
])

months = OrderedDict([
    ("января", 1), ("февраля", 2), ("марта", 3), ("апреля", 4), ("мая", 5),
    ("июня", 6), ("июля", 7), ("августа", 8), ("сентября", 9), ("октября", 10),
    ("ноября", 11), ("декабря", 12)
])

months_date = OrderedDict([
    (1, "Январь"), (2, "Февраль"), (3, "Март"), (4, "Апрель"), (5, "Май"),
    (6, "Июнь"), (7, "Июль"), (8, "Август"), (9, "Сентябрь"), (10, "Октябрь"),
    (11, "Ноябрь"), (12, "Декабрь")
])

loading_text = {
    "schedule": [
        "Загружаю", "Смотрю расписание", "Подождите, пожалуйста", "Ищу занятия",
        "Загружаю пары", "Жду ответ от сервера", "Сейчас спрошу у кого-нибудь"
    ],
    "ya_timetable": [
        "Загружаю", "Смотрю расписание", "Подождите, пожалуйста",
        "Жду ответ от сервера", "Смотрю на rasp.yandex.ru"
    ]
}

briefly_info_answer = \
    'КРАТКАЯ ИНФОРМАЦИЯ\n\n' \
    '<b>Раздел "Расписание"</b>\n' \
    'Здесь ты можешь <i>узнать расписание</i> на любой день, а также ' \
    '<i>подписаться на рассылку</i>.\n\n' \
    '<b>Раздел "{}"</b>\n' \
    'Здесь ты можешь <i>сменить группу</i> или <i>завершить работу</i> с ' \
    'ботом.\n\n' \
    '<b>Раздел "{}"</b>\n' \
    'Здесь ты можешь <i>оценить бота</i> и посмотреть <i>средний балл</i> ' \
    'оценок пользователей.\n\n' \
    '<b>Раздел "{}"</b>\n' \
    'Здесь ты можешь <i>скрыть</i> или <i>вернуть</i> занятие в расписании, ' \
    'а также настроить <i>отображение адреса</i>.\n\n' \
    '<b>Раздел "{}"</b>\n' \
    'Здесь ты можешь посмотреть <i>электрички</i> от или до Университета. ' \
    'Также есть возможность проложить <i>свой маршрут</i>.'.format(
        emoji["settings"], emoji["star"], emoji["editor"], emoji["suburban"])

special_thanks = \
    'ОСОБАЯ БЛАГОДАРНОСТЬ\n\n' \
    '@SuaiBot - идейный вдохновитель\n' \
    '<a href="https://rasp.yandex.ru">Яндекс.Расписания</a> - ' \
    '<a href="https://tech.yandex.ru/rasp/raspapi/">бесплатный API</a> ' \
    'для доступа к расписаниям электричек\n' \
    '<a href="https://it.spbu.ru">УСИТ СПбГУ</a> - предоставление ' \
    '<a href="https://timetable.spbu.ru/help">API</a> для доступа к ' \
    '<a href="https://timetable.spbu.ru">расписаниям занятий СПбГУ</a>\n'

weekend_answer = "{0} Выходной".format(emoji["sleep"])
week_off_answer = "{0} Выходная неделя".format(emoji["sleep"])
interval_exceeded_answer = "{0} Превышен интервал в <b>{1} дней</b>".format(
    emoji["warning"], max_answers_count
)
interval_off_answer = "{0} С <i>{1}</i> по <i>{2}</i> занятий нет"
ask_to_register_answer = "Чтобы пользоваться сервисом, необходимо " \
                      "зарегистрироваться.\nВоспользуйся коммандой /start"
student_required_answer = "Данная функция доступна только для студентов."
educator_required_answer = "Данная функция доступна только для преподавателей."
templates_answer = "Здесь ты можешь сохранять группы и преподавателей, чтобы " \
                   "быстро переключаться между расписаниями.\n" \
                   "Сейчас: <b>{0}</b>"
sending_info_answer = "Здесь ты можешь <b>подписаться</b> на рассылку " \
                      "расписания на следующий день или <b>отписаться</b> " \
                      "от неё.\nРассылка производится в 21:00"
sending_off_answer = "{0} Рассылка <b>отключена</b>".format(
    emoji["mailbox_off"]
)
sending_on_answer = "{0} Рассылка <b>активирована</b>\n" \
                    "Жди рассылку в 21:00".format(emoji["mailbox_on"])
ask_to_input_educator = "Введи Фамилию преподавателя: <i>(и И. О.)</i>"
personalization_answer = \
    "Здесь ты можешь настроить <b>домашнюю</b> и <b>Университетскую</b> " \
    "станции для команд <i>Домой</i> и <i>В Универ</i>\n\n" \
    "<b>Домашняя:</b> {0}\n<b>Университетская:</b> {1}"
select_home_station = "Выбери домашнюю станцию:"
select_univer_station = "Выбери университетскую станцию:"
yandex_error_answer = "Ошибка в обращении к серверу Яндекса. " \
                      "Попробуйте повторить позже."
yandex_segment_answer = "{time_mark} <i>Через</i> {lef_time}\n{train_mark} " \
                        "Отправление в <b>{dep_time}</b> ({arr_time}) " \
                        "<code>{price}{ruble_sign}</code>\n\n"
fast_trail_answer_select_day = "Начальная: <b>{from_title}</b>\n" \
                               "Кончная: <b>{to_title}</b>\nВыбери день:"
support_answer = "Если возникла проблема, то:\n" \
                 "1. Возможно, информация по этому поводу есть в нашем канале" \
                 " - @Spbu4u_news;\n" \
                 "2. Ты всегда можешь связаться с " \
                 "<a href='https://t.me/eeonedown'>разработчиком</a>."
main_menu_first_answer = \
    "Главное меню\n\n{0} - информация о боте\n{1} - оценить бота\n" \
    "{2} - настройки\n{3} - электрички\n{4} - <b>редактор расписания</b>\n" \
    "@Spbu4u_news - новости бота".format(
        emoji["info"], emoji["star"], emoji["settings"], emoji["suburban"],
        emoji["editor"]
    )
ask_to_input_educator_register = "Введи ФИО преподавателя:"
place_editor_answer = "Здесь ты можешь выбрать отображаемый формат адреса\n" \
                      "Сейчас: <b>{0}</b>"
changed_to_full_answer = "Теперь адрес отображается <b>полностью</b>"
changed_to_class_answer = "Теперь отображается <b>только аудитория</b>"
hide_answer = "Здесь ты можешь скрыть любое занятие\n" \
              "Выбери день, когда есть это занятие:"
hide_lesson_answer = "Выбери занятие, которое хочешь скрыть:"
selected_lesson_answer = "Занятие выбрано"
selected_lesson_info_answer = "День: {0}\nВремя: {1}\n" \
                              "Название: {3}\nПреподаватели: {4}\nТипы: Все"
updated_types_answer = "Типы обновлены"
ask_to_select_types_answer = "Укажи типы, которые хочешь скрыть:"
no_lessons_answer = "В этот день занятий нет."
how_to_hide_answer = "Как скрыть занятие?\nДень - Время- Преподаватель\n" \
                     "К - конкретный; Л - любой"
choose_answer = "Здесь ты можешь выбрать для отображения занятие или " \
                "преподавателя:"
ask_to_reset_answer = "Выбери, что ты хочешь вернуть:"
hidden_lessons_list_answer = "Вот список скрытых тобой занятий:\n\n"
chosen_educators_list_answer = "Вот список занятий с выбранными " \
                               "преподавателями:\n\n"
ask_to_select_lesson_answer = "Выбери то, которое хочешь вернуть:"
ask_to_select_edu_answer = "Выбери связь, которую хочешь убрать:"
no_hidden_lessons_answer = "Скрытых занятий нет"
no_chosen_educators_answer = "Скрытых преподавателей нет"
reset_all_lessons_answer = "Все занятия возвращены"
reset_lesson_answer = "Занятие <b>{0}</b> возвращено"
reset_educator_answer = "Связь <b>{0}</b> убрана"
full_reset_answer = "Все занятия и преподаватели возвращены"
reset_all_educators_answer = "Все преподаватели возвращены"
read_timeout_answer = "Превышено время ожидания ответа от timetable.spbu.ru. " \
                      "Возможно, сайт недоступен. Повторите позже."
connect_timeout_answer = "Не удается установить соединение с " \
                         "timetable.spbu.ru. Возможно, сайт недоступен. " \
                         "Повторите позже."
other_error_answer = "Кажется, произошла ошибка.\n" \
                     "Возможно, информация по этому поводу есть в нашем " \
                     "канале - @Spbu4u_news\nИ ты всегда можешь связаться с " \
                     "<a href='https://t.me/eeonedown'>разработчиком</a>"
ask_to_select_block_answer = "Выбери пару с большим количеством занятий:"
no_blocks_answer = "Нет пар с большим количеством занятий."
selectable_block_answer = "Вот список занятий, проходящих в данное время:\n\n"
ask_to_select_block_lesson_answer = "Выбери занятие, которое хочешь оставить:"

# groups: 0 - day, 3 - month, 5 - year
reg_before_30 = re.compile(r"^(0?[1-9]|[12]\d)((\.| )(0?[1-9]|1[012]|января|февраля|марта|апреля|мая|ию[нл]я|августа|сентября|октября|ноября|декабря)(\3(20(1[8-9]|[2-9]\d)))?)?$")
reg_only_30 = re.compile(r"^(30)((\.| )(0[13-9]|1[012]|января|марта|апреля|мая|ию[нл]я|августа|сентября|октября|ноября|декабря)(\3(20(1[8-9]|[2-9]\d)))?)?$")
reg_only_31 = re.compile(r"^(31)((\.| )(0[13578]|1[02]|января|марта|мая|июля|августа|октября|декабря)(\3(20(1[8-9]|[2-9]\d)))?)?$")
