from datetime import datetime

import django
import os
from openpyxl import load_workbook
import pandas as pd
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule_creator.settings")
django.setup()

from edu_resources.models import Room, Teacher, EduGroup, Lesson, Discipline, Week, LessonsFrom1c

file_xslx = os.path.join('расп0602.xlsx')

df = pd.read_excel(file_xslx)
df["Дата"].fillna(method="ffill", inplace=True)
# print(df)

# Преобразуем DataFrame в удобный формат
# Заполняем пропущенные даты сверху вниз
df["Дата"].fillna(method="ffill", inplace=True)

# Преобразуем DataFrame в удобный формат
schedule = []

for _, row in df.iterrows():
    date_str, day = row["Дата"].split('\n')[0], row["Дата"].split('\n')[1]

    time_range = row["Время"]

    # Преобразование даты и времени
    date = datetime.strptime(date_str, "%d.%m.%Y").date()
    print(date)
    start_time_str, finish_time_str = time_range.split(" - ")
    start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
    finish_time = datetime.strptime(finish_time_str, "%H:%M:%S").time()

    for group in df.columns[2:]:
        if len(group.split('.')[-1]) > 1:
            actual_group_id = EduGroup.objects.get(name=group).id
            # Пропускаем "Дата" и "Время"
            if pd.notna(row[group]):
                entry = row[group].split("\n")
                subject = entry[0]
                discipline_name = subject.split(' (')[0]
                discipline_type = subject.split(' (')[1].replace(')', '')

                if len(entry) > 1:
                    teachers = entry[1]
                    if len(teachers.split(', ')) == 1:
                        string_for_search = teachers.split(".")[0]
                        teachers_from_db = Teacher.objects.filter(name__startswith=string_for_search)
                        if teachers_from_db.count() > 1:
                            print(teachers)
                            print(subject)
                            print(teachers_from_db)
                            print('два препода в БД')
                            continue
                        elif teachers_from_db.count() < 1:
                            print(teachers)
                            print(subject)
                            print('нет такого преподавателя в БД')
                            continue
                        else:
                            actual_teacher_id = teachers_from_db[0].id
                    else:
                        print(teachers)
                        print(subject)
                        print('Два препода в расписании')
                        continue
                else:
                    teachers = ""
                    continue

                if len(entry) > 2:
                    room = entry[2]
                    actual_room = Room.objects.get(name=room)
                else:
                    room = ""

                lesson = {
                    "discipline": discipline_name,
                    "date": date,
                    "day": day,
                    "start": start_time,
                    "finish": finish_time,
                    "group": group,
                    "disc": subject,
                    "teachers": teachers,
                    "room": room
                }

                # matching_discipline = Discipline.objects.filter(name=discipline_name,
                #                                                 type=discipline_type,
                #                                                 teachers__id=actual_teacher_id,
                #                                                 groups__id=actual_group_id)


                # if matching_discipline.count() == 1:
                # actual_discipline = matching_discipline.first()
                # print(actual_discipline)
                actual_groop = EduGroup.objects.get(name=group)
                actual_week = Week.objects.filter(start_date__lte=date, finish_date__gte=date).first()
                new_lesson, created = LessonsFrom1c.objects.get_or_create(discipline=discipline_name,
                                                                   week=actual_week,
                                                                   day_of_week=day,
                                                                   date=date,
                                                                   start_time=start_time,
                                                                   finish_time=finish_time)
                if actual_room:
                    # print(teachers)
                    # print(actual_room)
                    new_lesson.room = actual_room
                    new_lesson.save()
                # disc_groups = actual_discipline.groups.all()
                new_lesson.groups.add(actual_groop)
                new_lesson.teachers.add(Teacher.objects.get(id=actual_teacher_id))

                # if lesson['group'] in ['23ПП-44.03.01.01-о2.3', '23ПП-44.03.01.01-о2.2', '23ПП-44.03.01.01-о2.1', '23ПП-44.03.01.01-о2']:
                # print(lesson['group'])
                # print('-------')
                # schedule.append(lesson)

# Преобразуем в DataFrame
# parsed_df = pd.DataFrame(schedule)
# print(parsed_df.head())