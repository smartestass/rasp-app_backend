import json
from collections import defaultdict
from functools import wraps

from django.core import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import EduGroup, Discipline, LessonPattern, Room, LessonsFrom1c, LessonFromHand, TeacherFromHand
from .models import Teacher, TeacherLimitation, Lesson, Week, User
from .serializers import LessonPatternSerializer, EduGroupSerializer, DisciplineSerializer, WeekSerializer
from .serializers import TeacherLimitationSerializer, LessonSerializer, ActualUserSerializer, Lesson1cSerializer
from rest_framework.decorators import api_view
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404, HttpResponse, JsonResponse
from datetime import datetime, date, timedelta
from django.core.paginator import Paginator
from django.db.models import Count
from django.contrib import messages as django_messages
from django.db.models import Value, CharField
from django.conf import settings
import os
import requests
import re
from django.contrib.auth import login


def get_next_sunday(start_date):
    """
    Возвращает ближайшее воскресенье, которое будет после или в ту же дату, что и start_date.
    """
    # Определяем день недели для start_date (0 - понедельник, 6 - воскресенье)
    day_of_week = start_date.isoweekday()
    print(day_of_week)

    # Если start_date уже воскресенье, возвращаем его
    if day_of_week == 7:
        return start_date
    else:
        # Иначе добавляем дни до следующего воскресенья
        days_until_sunday = 7 - day_of_week
        return start_date + timedelta(days=days_until_sunday)


@api_view(['GET'])
def get_dates_with_lessons(request, rasp_type, id):
    model_types = {'teacher': TeacherFromHand,
                   'group': EduGroup,
                   'room': Room}

    model_entity = model_types[rasp_type].objects.get(id=id)

    if rasp_type == 'teacher':
        lessons = LessonFromHand.objects.filter(teachers=model_entity).order_by('date')
    elif rasp_type == 'group':
        lessons = LessonFromHand.objects.filter(groups=model_entity).order_by('date')
    elif rasp_type == 'room':
        lessons = LessonFromHand.objects.filter(room=model_entity).order_by('date')
    else:
        lessons = {}
        return Response('нет данных')

    dates = set(lessons.values_list('date', flat=True))
    return Response(dates)


@api_view(['GET'])
def get_week_lessons(request, rasp_type, id):
    model_types = {'teacher': TeacherFromHand,
                   'group': EduGroup,
                   'room': Room}

    model_entity = model_types[rasp_type].objects.get(id=id)


    start_date_str = request.query_params.get('start_date')  # Формат: 'YYYY-MM-DD'

    if start_date_str:

        # Преобразуем строку в объект date
        start_date = date.fromisoformat(start_date_str)

    else:
        start_date = date.today()

    # Находим ближайшее воскресенье
    finish_date = get_next_sunday(start_date)
    print(finish_date)
    if rasp_type == 'teacher':
        lessons = LessonFromHand.objects.filter(teachers=model_entity, date__gte=start_date, date__lte=finish_date)
    elif rasp_type == 'group':
        lessons = LessonFromHand.objects.filter(groups=model_entity, date__gte=start_date, date__lte=finish_date)
    elif rasp_type == 'room':
        lessons = LessonFromHand.objects.filter(room=model_entity, date__gte=start_date, date__lte=finish_date)
    else:
        lessons = {}
        return Response('нет данных')

    # Передаем model_entity в контекст сериализатора
    serializer = Lesson1cSerializer(lessons, many=True, context={'model_entity': model_entity})
    data = serializer.data
    grouped_data = defaultdict(list)
    for item in data:
        act_date = item['date']
        grouped_data[act_date].append(item)

    # Преобразуем defaultdict в обычный dict для Response
    grouped_data = dict(grouped_data)

    return Response(grouped_data)


@api_view(['GET'])
def search(request, model, search_string):
    search_types = {'teacher': TeacherFromHand,
                    'group': EduGroup,
                    'room': Room}
    search_model = search_types[model]
    print(search_string)
    queryset = search_model.objects.filter(name__istartswith=search_string)
    print(queryset)
    search_data = json.loads(serializers.serialize('json', queryset, fields=['name']))
    return Response(search_data)


@api_view(['GET'])
def user_details(request, email):
    user = User.objects.get(email=email)
    user.last_login = datetime.now()
    serializer_data = ActualUserSerializer(user).data
    return Response(serializer_data)


# ms_identity_web = settings.MS_IDENTITY_WEB

# class CurriculumListView(APIView):
#     def get(self, request):
#         curricula = Curriculum.objects.all()
#         serializer = CurriculumSerializer(curricula, many=True)
#         return Response(serializer.data)

#
# @api_view(['GET'])
# def get_discipline_nagruzka(request, group_id, semester_id):
#     try:
#         # Получаем группу и семестр
#         group = EduGroup.objects.get(id=group_id)
#         semester = SemesterCurrent.objects.get(id=semester_id)
#
#         # Фильтруем дисциплины по группе и семестру
#         discipline_nagruzka = DisciplineNagruzka.objects.filter(
#             discipline_part__curriculum=group.curriculum,
#             discipline_part__semester=semester
#         )
#
#         # Сериализуем данные
#         serializer = DisciplineNagruzkaSerializer(discipline_nagruzka, many=True)
#
#         # Возвращаем данные в формате JSON
#         return Response(serializer.data)
#
#     except EduGroup.DoesNotExist:
#         return Response({'error': 'Group not found'}, status=404)
#
#     except SemesterCurrent.DoesNotExist:
#         return Response({'error': 'Semester not found'}, status=404)

#
# class GroupRowAPIView(APIView):
#     def get(self, request):
#         groups = EduGroup.objects.all()
#         serializer = GroupRowSerializer(groups, many=True)
#         return Response(serializer.data)


# class LessonPatternAPIView(APIView):
#     def get(self, request, group_id, semester_id):
#         group = EduGroup.objects.get(id=group_id)
#         semester = SemesterCurrent.objects.get(id=semester_id)
#
#         patterns = LessonPattern.objects.filter(discipline__discipline_part__curriculum=group.curriculum,
#                                                 discipline__discipline_part__semester=semester)
#
#         serializer = LessonPatternSerializer(patterns, many=True)
#         return Response(serializer.data)
#
#


# Представление для отображения списка групп
def group_selection_view(request):
    # print(request.user)
    forms = EduGroup.objects.values_list('form', flat=True).distinct()
    napravs = EduGroup.objects.values_list('naprav', flat=True).distinct()
    courses = EduGroup.objects.values_list('course', flat=True).distinct()

    if request.GET.get('action') == 'submit':
        form = request.GET.get('form')
        course = request.GET.get('course')
        naprav = request.GET.get('naprav')
        groups = EduGroup.objects.filter(form=form,
                                         course=course,
                                         naprav=naprav)
        serializer = EduGroupSerializer(groups, many=True)
    else:
        groups = EduGroup.objects.all()
        serializer = EduGroupSerializer(groups, many=True)
    return render(request, 'edu_resources/group_selection.html', {'groups': serializer.data,
                                                                  'forms': forms,
                                                                  'courses': courses,
                                                                  'napravs': napravs,
                                                                  })


# Тайминги и дни недели
TIME_SLOTS = [
    '08:00 - 09:35',
    '09:50 - 11:25',
    '11:55 - 13:30',
    '13:45 - 15:20',
    '15:50 - 17:25',
    '17:35 - 19:10',
    '19:15 - 20:50',
]
DAYS = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']


def date_format(time_slot):
    time_start_str, time_finish_str = time_slot.replace(' ', '').split('-')
    time_start = datetime.strptime(time_start_str, '%H:%M')
    time_finish = datetime.strptime(time_finish_str, '%H:%M')
    return time_start, time_finish


# # Представление для создания расписания
# def create_schedule_view(request, group_id):
#     if request.method == 'POST':
#         if request.POST.get('action') == 'submit':
#             discipline_id = request.POST.get('discipline_id')
#             day = request.POST.get('day').lower()
#
#             time_start, time_finish = date_format(request.POST.get('time_slot'))
#
#             LessonPattern.objects.create(discipline_id=int(discipline_id),
#                                          day=day,
#                                          time_start=time_start,
#                                          time_finish=time_finish)
#
#         if request.POST.get('action') == 'delete':
#             lesson_pattern_id = request.POST.get('lesson_id')
#             LessonPattern.objects.filter(id=lesson_pattern_id).delete()
#
#         return redirect('create_schedule', group_id=group_id)
#
#     actual_teacher_patterns = []
#     discipline_name = 'Нет дисциплины'
#     discipline_id = request.GET.get('discipline_id')
#     group_name = EduGroup.objects.get(id=group_id).name
#     limitations = []
#
#     if discipline_id:
#         teacher_id = DisciplineNagruzka.objects.get(id=discipline_id).teacher_id
#         teacher_patterns = LessonPattern.objects.filter(discipline__teacher_id=teacher_id)
#         actual_teacher_patterns = LessonPatternSerializer(teacher_patterns, many=True).data
#         discipline_name = DisciplineNagruzka.objects.get(id=discipline_id).discipline_part.discipline.name
#         limitations = TeacherLimitationSerializer(TeacherLimitation.objects.filter(teacher=teacher_id), many=True).data
#
#     group = EduGroup.objects.get(id=group_id)
#     semester = SemesterCurrent.objects.get(curriculum__groups=group, start_date__year=2025)
#     disciplines = DisciplineNagruzka.objects.filter(discipline_part__curriculum__groups=group,
#                                                     discipline_part__semester=semester)
#     serializer = DisciplineNagruzkaSerializer(disciplines, many=True)
#     actual_patterns = LessonPattern.objects.filter(discipline__discipline_part__semester=semester,
#                                                    discipline__discipline_part__curriculum__groups=group)
#
#     schedule_patterns = LessonPatternSerializer(actual_patterns, many=True).data
#
#     # Создаём структуру для таблицы
#     timetable = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}
#
#     timetable_with_limitations = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}
#     fill_timetable(timetable_with_limitations, DAYS, limitations)
#
#     fill_timetable(timetable, DAYS, schedule_patterns)
#     fill_timetable(timetable, DAYS, actual_teacher_patterns)
#
#     return render(request, 'edu_resources/create_schedule.html', {
#         'timetable': timetable,
#         'timetable_limitations': timetable_with_limitations,
#         'time_slots': TIME_SLOTS,
#         'days': DAYS,
#         'disciplines': serializer.data,
#         'group_id': group_id,
#         'discipline_id': discipline_id,
#         'discipline_name': discipline_name,
#         'group_name': group_name
#     })


# def choice_group_view(request):
#     groups = EduGroup.objects.filter(curriculum__semesters__start_date__year=2025)
#     return render(request, )


def get_dates_for_weekdays(start_date, days=None):
    if days is None:
        days = DAYS

    dates = {}
    days_to_append = 0
    for day in days:
        dates[day] = (start_date + timedelta(days=days_to_append)).strftime('%d.%m.%Y')
        days_to_append += 1
    return dates


def get_time_slot(time):
    """Определяем тайминг по времени начала занятия."""
    if time >= '08:00' and time < '09:35':
        return '08:00 - 09:35'
    elif time >= '09:50' and time < '11:25':
        return '09:50 - 11:25'
    elif time >= '11:55' and time < '13:30':
        return '11:55 - 13:30'
    elif time >= '13:45' and time < '15:20':
        return '13:45 - 15:20'
    elif time >= '15:50' and time < '17:25':
        return '15:50 - 17:25'
    elif time >= '17:35' and time < '19:10':
        return '17:35 - 19:10'
    elif time >= '19:15' and time < '20:50':
        return '19:15 - 20:50'
    return None


def fill_timetable(timetable, days, patterns, whose_lessons=False):
    for pattern in patterns:
        time_slot = get_time_slot(pattern['time_start'])
        day = pattern['day'].lower()
        if time_slot and day in days:
            if not pattern in timetable[time_slot][day]:
                if whose_lessons:
                    pattern['conflict'] = whose_lessons
                    print(pattern)
                timetable[time_slot][day].append(pattern)


@settings.AUTH.login_required(scopes=["User.Read"])
def teacher_limitations_view(request, *, context):
    user = context['user']
    # print(context)
    token = context['access_token']

    if user:
        url = f'https://graph.microsoft.com/v1.0/users?$filter=displayName eq \'Вороная Виктория Дмитриевна\''

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        users = response.json()
        print("Users found:", users)

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')

        if request.POST.get('action') == 'append':
            day = request.POST.get('day')
            time_start, time_finish = date_format(request.POST.get('time_slot'))

            TeacherLimitation.objects.create(teacher_id=teacher_id,
                                             day=day,
                                             time_start=time_start,
                                             time_finish=time_finish)

        if request.POST.get('action') == 'delete':
            limitation_id = request.POST.get('limitation_id')
            TeacherLimitation.objects.get(id=limitation_id).delete()

        return redirect(f'{reverse("limitation")}?entity_id={teacher_id}')

    entity_id = request.GET.get('entity_id')
    entities = Teacher.objects.all()
    limitations = TeacherLimitationSerializer(TeacherLimitation.objects.filter(teacher=entity_id),
                                              many=True).data
    timetable = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}
    fill_timetable(timetable, DAYS, limitations)
    # print(timetable)

    return render(request, 'edu_resources/limitations.html',
                  {'timetable': timetable,
                   'time_slots': TIME_SLOTS,
                   'days': DAYS,
                   'entity_id': entity_id,
                   'entities': entities,
                   'user': user
                   })


@settings.AUTH.login_required(scopes=['User.Read'])
def authorization(request, *, context):
    user = context['user']


@settings.AUTH.login_required(scopes=['User.Read'])
def schedule_view_new(request, schedule_type, group_id=None, *, context):
    # Получаем группу, если она не передана, используем группу по умолчанию
    if not group_id:
        group = EduGroup.objects.get(id=12)
    else:
        group = EduGroup.objects.get(id=group_id)

    # Получаем недели для выбранной группы
    weeks = Week.objects.all().order_by('order_number')
    paginator = Paginator(weeks, 1)

    # Получаем номер страницы из GET-запроса
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Получаем текущую неделю
    current_week = page_obj.object_list[0] if page_obj.object_list else None
    week_number = current_week.order_number if current_week else None

    # Получаем даты для текущей недели
    dates = get_dates_for_weekdays(current_week.start_date) if current_week else {}

    # Инициализация переменных для учителей, групп и паттернов
    teachers = Teacher.objects.all()
    groups = EduGroup.objects.all()
    entity_name = 'Нет имени'
    patterns = []
    entities = []

    # Логика для типа расписания "teacher"
    if schedule_type == 'teacher':
        entities = Teacher.objects.all()
        entity_id = request.GET.get('entity_id', 1)

        # Если entity_id указан, получаем имя учителя и соответствующие уроки
        if entity_id:
            try:
                teacher = Teacher.objects.get(id=entity_id)
                entity_name = teacher.name
                pattern_objects = Lesson.objects.filter(discipline__teacher_id=entity_id,
                                                        week__order_number=week_number)
                patterns = LessonSerializer(pattern_objects, many=True).data
            except Teacher.DoesNotExist:
                entity_name = 'Не найдено'

    # Логика для типа расписания "group"
    elif schedule_type == 'group':
        entities = EduGroup.objects.all()
        # print(request.GET.get('entity_id'))
        entity_id = request.GET.get('entity_id')

        # Если entity_id указан, получаем имя группы и соответствующие уроки
        if entity_id:
            try:
                group_obj = EduGroup.objects.get(id=entity_id)
                entity_name = group_obj.name
                pattern_objects = Lesson.objects.filter(discipline__groups__id=entity_id,
                                                        week=current_week)
                patterns = LessonSerializer(pattern_objects, many=True).data
            except EduGroup.DoesNotExist:
                entity_name = 'Не найдено'

    # Если тип расписания не определен, возвращаем ошибку
    else:
        return render(request, 'edu_resources/schedule_view_new.html', {'error': 'Некорректный тип расписания'})

    # Формирование расписания
    timetable = {day: {time_slot: [] for time_slot in TIME_SLOTS} for day in DAYS}
    fill_timetable(timetable, DAYS, patterns)
    print(timetable)

    # Рендеринг страницы с переданными данными
    return render(request, 'edu_resources/schedule_view_new.html',
                  {'entity_id': entity_id,
                   'entity_name': entity_name,
                   'patterns': patterns,
                   'entities': entities,
                   'days': DAYS,
                   'time_slots': TIME_SLOTS,
                   'timetable': timetable,
                   'schedule_type': schedule_type,
                   'page_obj': page_obj,
                   'dates': dates})


#
#     teachers = Teacher.objects.all()
#     teacher_id = request.GET.get('teacher_id')
#     print(teacher_id)
#     teacher_name = 'Нет имени'
#     if teacher_id:
#         teacher_name = Teacher.objects.get(id=teacher_id).name
#
#     pattern_objects = LessonPattern.objects.filter(discipline__teacher_id=teacher_id)
#     patterns = LessonPatternSerializer(pattern_objects, many=True).data
#
#     timetable = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}
#
#     fill_timetable(timetable, DAYS, patterns)
#
#     return render(request, 'edu_resources/schedule_view.html',
#                   {'teacher_id': teacher_id,
#                    'teacher_name': teacher_name,
#                    'patterns': patterns,
#                    'teachers': teachers,
#                    'days': DAYS,
#                    'time_slots': TIME_SLOTS,
#                    'timetable': timetable,})
#
#
# def group_schedule_view(request, group_id, semester_id):
#
#     groups = Teacher.objects.all()
#     group_id = request.GET.get('group_id')
#     group_name = 'Нет имени'
#     if group_id:
#         group_name = EduGroup.objects.get(id=group_id).name
#
#     LessonPattern.objects.filter(discipline__discipline_part__semester=semester,
#                                  discipline__discipline_part__curriculum__groups=group)
#     patterns = LessonPatternSerializer(pattern_objects, many=True).data
#
#     timetable = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}
#
#     fill_timetable(timetable, DAYS, patterns)
#
#     return render(request, 'edu_resources/schedule_view.html',
#                   {'teacher_id': teacher_id,
#                    'teacher_name': teacher_name,
#                    'patterns': patterns,
#                    'teachers': teachers,
#                    'days': DAYS,
#                    'time_slots': TIME_SLOTS,
#                    'timetable': timetable,})


def edit_real_schedule(request, group_id):
    group = EduGroup.objects.get(id=group_id)
    group_name = group.name
    # weeks = Week.objects.filter(group=group).order_by('order_number')

    weeks = Week.objects.all()
    paginator = Paginator(weeks, 1)

    page_number = request.GET.get('page', 1)

    page_obj = paginator.get_page(page_number)

    # Получаем ID текущей недели
    current_week = page_obj.object_list[0] if page_obj.object_list else None

    week_start_date = current_week.start_date
    week_finish_date = current_week.finish_date
    week_number = current_week.order_number
    week_id = current_week.id

    dates = get_dates_for_weekdays(current_week.start_date)

    # semester = SemesterCurrent.objects.get(curriculum__groups=group, start_date__year=2025)

    disciplines_solo = Discipline.objects.annotate(group_count=Count('groups')).filter(group_count=1,
                                                                                       groups=group)

    disciplines_with_others = Discipline.objects.annotate(group_count=Count('groups')).filter(group_count__gt=1,
                                                                                              groups=group)

    related_groups = EduGroup.objects.filter(discipline__in=disciplines_with_others).exclude(id=group_id).distinct()

    related_groups_serialized = EduGroupSerializer(related_groups, many=True).data

    serialized_other_groups_lessons = []

    disciplines_solo_serialized = DisciplineSerializer(disciplines_solo, many=True).data
    disciplines_with_others_serialized = DisciplineSerializer(disciplines_with_others, many=True).data

    actual_teacher_lessons = []
    discipline_name = 'Нет дисциплины'
    discipline_id = request.GET.get('discipline_id')
    limitations = []
    actual_lessons = Lesson.objects.filter(groups__id=group_id,
                                           week=current_week)

    serialized_lessons = LessonSerializer(actual_lessons, many=True).data
    # print(serialized_lessons)

    # for l in serialized_lessons:
    #     l['conflict'] = ''

    serialized_teacher_lessons = []
    serialized_other_lessons = []

    if discipline_id:
        discipline_id = int(discipline_id)
        teachers = Discipline.objects.get(id=discipline_id).teachers.all()
        teacher_lessons = Lesson.objects.filter(week__order_number=week_number,
                                                discipline__teachers__in=teachers)
        serialized_teacher_lessons = LessonSerializer(teacher_lessons, many=True).data

        # for teacher_lesson in serialized_teacher_lessons:
        #     teacher_lesson['conflict'] = 'prep'

        # print(serialized_teacher_lessons)
        discipline_name = Discipline.objects.get(id=discipline_id).name
        limitations = TeacherLimitationSerializer(TeacherLimitation.objects.filter(teacher__in=teachers),
                                                  many=True).data
        other_groups = Discipline.objects.get(id=discipline_id).groups.exclude(id=group_id)
        if other_groups:
            other_groups_lessons = Lesson.objects.filter(week__order_number=week_number,
                                                         groups__in=other_groups).exclude(groups__id=group_id)
            serialized_other_lessons = LessonSerializer(other_groups_lessons, many=True).data
            # for other_lesson in serialized_other_lessons:
            #     other_lesson['conflict'] = 'group'

    timetable = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}

    timetable_with_limitations = {time_slot: {day: [] for day in DAYS} for time_slot in TIME_SLOTS}
    fill_timetable(timetable_with_limitations, DAYS, limitations)

    fill_timetable(timetable, DAYS, serialized_lessons)
    fill_timetable(timetable, DAYS, serialized_teacher_lessons, whose_lessons='teacher')
    fill_timetable(timetable, DAYS, serialized_other_lessons, whose_lessons='group')
    # for timing, info in timetable.items():
    #     print(timing)
    #     print(info)
    if request.method == 'POST':

        page_number = request.POST.get('page')
        page_obj = paginator.get_page(page_number)
        discipline_id = request.POST.get('discipline_id', 1)

        if request.POST.get('action') == 'post_room':
            lesson_id = request.POST.get('lesson_id')
            # actual_room = Room.objects.get(id=)
            lesson_object = Lesson.objects.get(id=lesson_id)
            lesson_object.room_id = request.POST.get('room_id')
            lesson_object.save()
            return redirect(
                f'{reverse("edit_real_schedule", args=[group_id])}?page={page_number}')

        if request.POST.get('action') == 'submit':
            current_disc = Discipline.objects.get(id=discipline_id).groups.all()

            day = request.POST.get('day').lower()
            time_start, time_finish = date_format(request.POST.get('time_slot'))
            date = datetime.strptime(request.POST.get('date'), '%d.%m.%Y')
            week_id = request.POST.get('week')
            week_number = Week.objects.get(id=week_id).order_number

            lesson, created = Lesson.objects.get_or_create(week_id=week_id,
                                                           discipline_id=discipline_id,
                                                           day_of_week=day,
                                                           date=date,
                                                           start_time=time_start,
                                                           finish_time=time_finish)
            disc_groups = Discipline.objects.get(id=discipline_id).groups.all()
            lesson.groups.add(*disc_groups)

            return redirect(
                f'{reverse("edit_real_schedule", args=[group_id])}?page={page_number}&discipline_id={discipline_id}')

        if request.POST.get('action') == 'delete':
            lesson_id = request.POST.get('lesson_id')
            # discipline_id = Lesson.objects.get(id=lesson_id).discipline_id
            Lesson.objects.get(id=lesson_id).delete()

            return redirect(
                f'{reverse("edit_real_schedule", args=[group_id])}?page={page_number}')

        if request.POST.get('action') == 'copy':

            current_week = Week.objects.get(id=request.POST.get('week'))
            # print(current_week)
            week_number = int(current_week.order_number)
            next_week = Week.objects.get(order_number=week_number + 1)

            lessons_to_copy = Lesson.objects.filter(week_id=current_week.id,
                                                    groups__id=group_id)

            conflicts = []
            for lesson in lessons_to_copy:
                new_date = lesson.date + timedelta(days=7)

                groups = lesson.groups.all()
                for g in groups:
                    lessons = Lesson.objects.filter(week_id=next_week.id,
                                                    day_of_week=lesson.day_of_week,
                                                    date=new_date,
                                                    start_time=lesson.start_time,
                                                    finish_time=lesson.finish_time,
                                                    groups__id=g.id)
                    if lessons:
                        for l in lessons:
                            conflicts.append(l)
            if not conflicts:
                for lesson in lessons_to_copy:
                    new_date = lesson.date + timedelta(days=7)
                    new_lesson, created = Lesson.objects.get_or_create(week=next_week,
                                                                       day_of_week=lesson.day_of_week,
                                                                       discipline=lesson.discipline,
                                                                       date=new_date,
                                                                       start_time=lesson.start_time,
                                                                       finish_time=lesson.finish_time)
                    disc_groups = Discipline.objects.get(id=lesson.discipline_id).groups.all()
                    new_lesson.groups.add(*disc_groups)
            else:
                messages = []
                for c in conflicts:
                    conflict_groups = []
                    for confl_gr in c.groups.all():
                        conflict_groups.append(confl_gr.name)
                    message = f'Конфликт: {c.discipline} ({c.day_of_week}, {c.start_time}). Группы {"".join(conflict_groups)}'
                    messages.append(message)

                django_messages.warning(request, ''.join(messages))
                return redirect(
                    f'{reverse("edit_real_schedule", args=[group_id])}?page={int(page_number)}')
            return redirect(
                f'{reverse("edit_real_schedule", args=[group_id])}?page={int(page_number) + 1}')

    return render(request, 'edu_resources/create_schedule_new.html', {
        'timetable': timetable,
        'timetable_limitations': timetable_with_limitations,
        'time_slots': TIME_SLOTS,
        'days': DAYS,
        'disciplines_solo': disciplines_solo_serialized,
        'disciplines_with_others': disciplines_with_others_serialized,
        'group_id': group_id,
        'discipline_id': discipline_id,
        'discipline_name': discipline_name,
        'group_name': group_name,
        'start_date': week_start_date,
        'finish_date': week_finish_date,
        'week_number': week_number,
        'dates': dates,
        'page_obj': page_obj,
        'week_id': week_id,
        'related_groups': related_groups_serialized,
    })


# def create_schedule_pdf(group):
#     timetable = []
#     lessons = Lesson.objects.filter(week__group=group)
#         for day in DAYS:
#             weekday_lessons = lessons.filter(day_of_week=day)


def append_lesson(group_id, discipline_id, day, date, time_start, time_finish, week_number):
    current_week_id = Week.objects.get(group_id=group_id,
                                       order_number=week_number).id
    Lesson.objects.get_or_create(week_id=current_week_id,
                                 discipline_id=discipline_id,
                                 day_of_week=day,
                                 date=date,
                                 start_time=time_start,
                                 finish_time=time_finish)


# @settings.AUTH.login_required(scopes=["User.Read"])
# def get_or_create_django_user(request,)


@settings.AUTH.login_required(scopes=["User.Read"])
def create_student_users(request, *, context):
    token = context['access_token']
    groups = EduGroup.objects.all()

    for group_object in groups:
        name = group_object.name
        print(name)

        url = f"https://graph.microsoft.com/v1.0/groups?$filter=startswith(displayName, '{name}')"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        groups_response = response.json()
        id = groups_response['value'][0]['id']

        url = f"https://graph.microsoft.com/v1.0/groups/{id}/members"

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        members_response = response.json()

        for student in members_response["value"]:
            student_name = student['displayName']
            student_email = student['mail']

            student_object, created = User.objects.get_or_create(first_name=student_name,
                                                                 email=student_email,
                                                                 username=student_email)
            if created:
                student_object.user_type = 'student'
            else:
                if student_object.user_type == 'teacher':
                    print(f'{student_object} уже есть в БД')
                    student_object.user_type = 'mix'
            student_object.edu_group = group_object
            student_object.save()
            print(student_object.first_name)

    return HttpResponse('готово')


@settings.AUTH.login_required(scopes=["User.Read"])
def create_teacher_users(request, *, context):
    # username = context['user']['name']
    # email = context['user']['preferred_username']
    # short_name_list = context['user']['name'].split(' ')
    # short_name = f'{short_name_list[0]}. {short_name_list[1]}. {short_name_list[2]}.'
    #
    # teacher = User.objects.get(username=username,
    #                            email=email,
    #                            short_name=short_name)
    # if teacher:
    #     login(request, teacher)
    #     url = reverse('rasp_teacher')
    #     return redirect(f'{url}?entity_id={teacher.teacher_id}')
    # print(context)
    token = context['access_token']
    teachers = TeacherFromHand.objects.all()

    for teacher_object in teachers:
        name = re.sub(r'\s?\([^)]*\)\s*', ' ', teacher_object.name).strip()
        str_for_search = name.split('.')[0]
        print(name)
        # print(str_for_search)

        url = f"https://graph.microsoft.com/v1.0/users?$filter=startswith(displayName, '{str_for_search}')"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        users = response.json()

        # print(users)

        if len(users) > 2:
            print('больше двух')
            print(users)
        else:
            try:
                email = users['value'][0]['mail']
            except IndexError:
                print('нет емайла')
                continue
            user_object, created = User.objects.get_or_create(username=email,
                                                              email=email,
                                                              user_type='teacher',
                                                              teacher=teacher_object,
                                                              first_name=name)
            if created:
                user_object.set_unusable_password()
                user_object.save()
    return HttpResponse('готово')


def role_choosing(request):
    if request.method == 'POST':
        if request.POST.get('role') == 'teacher':
            return redirect('teacher_schedule')
        elif request.POST.get('role') == 'student':
            return redirect('student_schedule')
    return render(request, 'edu_resources/role_choosing.html')


def custom_login_required(scopes=None, redirect_url='home'):
    def decorator(view_func):
        @wraps(view_func)
        @settings.AUTH.login_required(scopes=scopes)
        def wrapped_view(*args, context, **kwargs):
            # Вызов оригинальной view-функции
            response = view_func(*args, context=context, **kwargs)

            # Проверка, аутентифицирован ли пользователь
            user = context['user']
            if user:
                print(user)
                return redirect(redirect_url)

            # Возвращаем оригинальный response
            return response

        return wrapped_view

    return decorator


def find_user_for_teacher(request, name, email):
    current_user = User.objects.get(username=name,
                                    email=email,
                                    user_type='prep')
    if current_user:
        login(request, current_user)
        url = reverse('rasp_teacher')
        return {'role': 'teacher',
                'redirect': f'{url}?entity_id={current_user.teacher_id}'}
    return None


@settings.AUTH.login_required(scopes=["User.Read"])
def redirect_to_schedule(request, *, context):
    teacher_user = find_user_for_teacher(request,
                                         context['user']['name'],
                                         context['user']['preferred_username'])
    if teacher_user:
        print(f'{teacher_user} !!!')
        return redirect(teacher_user['redirect'])


# @settings.AUTH.login_required(scopes=["User.Read"])
@settings.AUTH.login_required(scopes=["User.Read"])
def view_schedule(request, schedule_type, *, context):
    entity_id = request.GET.get('entity_id')
    if not entity_id:
        current_user = User.objects.get(id=request.user.id)
        if current_user.user_type == 'prep':
            # teacher_id = User.objects.get(id=request.user.id).teacher_id
            entity_id = current_user.teacher_id
        elif current_user.user_type == 'student':
            entity_id = current_user.edu_group_id

    # Получаем недели для выбранной группы
    weeks = Week.objects.all().order_by('order_number')
    paginator = Paginator(weeks, 1)

    current_order_week = get_current_week_order()

    # Получаем номер страницы из GET-запроса
    page_number = request.GET.get('page', current_order_week)
    page_obj = paginator.get_page(page_number)

    # Получаем текущую неделю
    current_week = page_obj.object_list[0] if page_obj.object_list else None

    week_info = WeekSerializer(current_week).data

    week_number = current_week.order_number if current_week else None

    if schedule_type == 'teacher':
        lessons = Lesson.objects.filter(discipline__teacher_id=entity_id, week__order_number=week_number).order_by(
            'date')
    elif schedule_type == 'group':
        group_id = request.GET.get('entity_id')
        lessons = Lesson.objects.filter(groups__id=group_id, week__order_number=week_number)
    else:
        lessons = []
        lessons_dict = {}
    lessons_dict = generate_lessons(lessons)
    print(lessons_dict)
    return render(request, 'edu_resources/rasp.html', {'lessons': lessons_dict,
                                                       'page_obj': page_obj,
                                                       'schedule_type': schedule_type,
                                                       'entity_id': entity_id,
                                                       'week': week_info})


def generate_lessons(lessons):
    uniq_days = lessons.values_list('day_of_week', flat=True).distinct()

    lessons_dict = {}

    for day in uniq_days:
        lessons_dict[day.capitalize()] = LessonSerializer(lessons.filter(day_of_week=day).order_by('start_time'),
                                                          many=True, exclude=['available_rooms',
                                                                              'teacher_short_name']).data
    return lessons_dict


def get_current_week_order():
    # Получаем текущую дату
    today = datetime.today()

    # Определяем номер дня недели (понедельник = 0, воскресенье = 6)
    weekday = today.weekday()

    # Вычисляем дату понедельника текущей недели
    monday = today - timedelta(days=weekday)

    try:
        current_order = Week.objects.get(start_date=monday)
    except Week.DoesNotExist:
        return 1

    return current_order.order_number
