import datetime

from rest_framework import serializers
from .models import *
import re
from django.db.models import Q


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        # Получаем список исключаемых полей из аргументов
        exclude_fields = kwargs.pop('exclude', None)
        super().__init__(*args, **kwargs)

        if exclude_fields is not None:
            # Удаляем указанные поля из полей сериализатора
            for field in exclude_fields:
                self.fields.pop(field, None)


class EduGroupSerializer(serializers.ModelSerializer):
    count_of_disciplines = serializers.SerializerMethodField()

    class Meta:
        model = EduGroup
        fields = ['id', 'name', 'work_plan', 'form', 'course', 'naprav', 'profile', 'size', 'count_of_disciplines']

    def get_count_of_disciplines(self, obj):
        disciplines_count = obj.discipline_set.all().count()
        return disciplines_count


class DisciplineSerializer(serializers.ModelSerializer):
    count_of_lessons = serializers.SerializerMethodField()
    teacher_names = serializers.StringRelatedField(source='teachers', many=True)
    type = serializers.SerializerMethodField()
    group_names = serializers.StringRelatedField(source='groups', many=True)
    lessons_in_schedule = serializers.SerializerMethodField()

    class Meta:
        model = Discipline
        fields = ['id', 'name', 'hours', 'myam', 'teachers', 'count_of_lessons', 'teacher_names', 'type',
                  'group_names', 'lessons_in_schedule']

    def get_count_of_lessons(self, obj):
        count = int(round(obj.hours / 2))
        return count

    def get_type(self, obj):
        actual_type = obj.type
        if actual_type == 'Лабораторные':
            return actual_type[:3].upper()
        else:
            return actual_type[:4].upper()

    def get_lessons_in_schedule(self, obj):
        lessons = int(Lesson.objects.filter(discipline=obj).count())
        return lessons




# class SemesterCurrentSerializer(serializers.ModelSerializer):
#     semester_name = serializers.SerializerMethodField()
#
#     class Meta:
#         model = SemesterCurrent
#         fields = ['semester', 'semester_name', 'start_date']
#
#     def get_semester_name(self, obj):
#         return obj.semester.name

#
# class CurriculumSerializer(serializers.ModelSerializer):
#     groups = EduGroupSerializer(many=True, read_only=True)
#     semesters = serializers.SerializerMethodField()
#
#     class Meta:
#         model = Curriculum
#         fields = ['name', 'code', 'start_date', 'groups', 'semesters']
#
#     def get_semesters(self, obj):
#         # Фильтрация семестров с начальной датой 2024 года
#         semesters = obj.semesters.filter(start_date__year=2024)
#         return SemesterCurrentSerializer(semesters, many=True).data


# class DisciplineNagruzkaSerializer(serializers.ModelSerializer):
#     discipline_name = serializers.CharField(source='discipline_part.discipline.name', read_only=True)
#     discipline_type = serializers.CharField(source='discipline_part.type.name', read_only=True)
#     teacher_name = serializers.CharField(source='teacher.name', read_only=True)
#
#     class Meta:
#         model = DisciplineNagruzka
#         fields = ['id', 'teacher', 'discipline_name', 'discipline_type', 'teacher_name', 'hours']


# class DisciplineSerializer(serializers.ModelSerializer):
#     discipline_name = serializers.CharField(source='discipline_part.discipline.name', read_only=True)
#     discipline_type = serializers.CharField(source='discipline_part.type.name', read_only=True)
#     teacher_name = serializers.CharField(source='teacher.name', read_only=True)
#     lessons_in_schedule_count = serializers.SerializerMethodField()
#     lessons_count = serializers.SerializerMethodField()
#
#     class Meta:
#         model = DisciplineNagruzka
#         fields = ['id', 'teacher', 'discipline_name',
#                   'discipline_type', 'teacher_name', 'hours',
#                   'lessons_count', 'lessons_in_schedule_count']
#
#     def get_lessons_in_schedule_count(self, obj):
#         lessons_count = Lesson.objects.filter(
#             week__discipline__discipline_part__curriculum=obj.curriculum
#         ).count()
#         return lessons_count
#
#     def get_lessons_count(self, obj):
#         return int(obj.hours / 2)



# class GroupRowSerializer(serializers.ModelSerializer):
#     current_semester_name = serializers.SerializerMethodField()
#     current_semester_id = serializers.SerializerMethodField()
#     hours = serializers.SerializerMethodField()
#     # hours_on_schedule = serializers.SerializerMethodField()
#     disciplines = serializers.SerializerMethodField()
#
#     class Meta:
#         model = EduGroup
#         fields = ['id', 'name', 'current_semester_name', 'current_semester_id', 'hours', 'disciplines']
#
#     def get_current_semester_name(self, obj):
#         semester = obj.curriculum.semesters.filter(start_date__year=2025).first()
#         return semester.semester.name if semester else "Не задано"
#
#     def get_current_semester_id(self, obj):
#         semester = obj.curriculum.semesters.filter(start_date__year=2025).first()
#         return semester.semester.pk if semester else "Не задано"
#
#     def get_hours(self, obj):
#         return DisciplineNagruzka.objects.filter(
#             discipline_part__curriculum=obj.curriculum
#         ).aggregate(total_hours=models.Sum('hours'))['total_hours'] or 0
#
#     # def get_hours_on_schedule(self, obj):
#     #     lessons_count = Lesson.objects.filter(
#     #         week__discipline__discipline_part__curriculum=obj.curriculum
#     #     ).count()
#     #     return lessons_count * 2
#
#     def get_disciplines(self, obj):
#         disciplines = DisciplineNagruzka.objects.filter(
#             discipline_part__curriculum=obj.curriculum
#         ).values_list('discipline_part__discipline', flat=True).distinct()
#         return disciplines.count()


class LessonPatternSerializer(serializers.ModelSerializer):
    discipline_name = serializers.CharField(source='discipline.discipline_part.discipline.name', read_only=True)
    discipline_type = serializers.CharField(source='discipline.discipline_part.type')
    hours = serializers.CharField(source='discipline.hours')
    teacher = serializers.CharField(source='discipline.teacher')
    teacher_id = serializers.CharField(source='discipline.teacher.id')
    group_name = serializers.SerializerMethodField()
    group_id = serializers.SerializerMethodField()

    class Meta:
        model = LessonPattern
        fields = ['id', 'discipline_name', 'discipline_type', 'hours', 'teacher', 'day', 'time_start', 'group_name',
                  'group_id', 'teacher_id']

    def get_group_name(self, obj):
        group = EduGroup.objects.get(curriculum_id=obj.discipline.discipline_part.curriculum_id)
        return group.name

    def get_group_id(self, obj):
        group = EduGroup.objects.get(curriculum_id=obj.discipline.discipline_part.curriculum_id)
        return group.id


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EduGroup
        fields = ['id', 'name']


class TeacherFromHandSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherFromHand
        fields = ['id', 'name']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']

class Lesson1cSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()
    teachers = TeacherFromHandSerializer(many=True)
    timing = serializers.SerializerMethodField()
    russian_date = serializers.SerializerMethodField()
    room = RoomSerializer()

    class Meta:
        model = LessonFromHand
        fields = ['id', 'discipline', 'date', 'russian_date', 'teachers', 'groups', 'timing',
                  'room', 'lesson_type']

    def get_russian_date(self, obj):
        months = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        str_date = f"{obj.date.day} {months[obj.date.month]}"
        return str_date

    def get_timing(self, obj):
        start, finish = obj.start_time, obj.finish_time
        timing = f"{start.strftime('%H:%M')} - {finish.strftime('%H:%M')}"
        return timing

    def get_groups(self, obj):
        groups = obj.groups.all()
        model_entity = self.context.get('model_entity')  # Получаем model_entity из контекста
        if model_entity and isinstance(model_entity, EduGroup):
            # Если model_entity является группой, перемещаем её в начало списка
            groups = sorted(groups, key=lambda x: x.id != model_entity.id)
        return GroupSerializer(groups, many=True).data

    # def get_room_info(self, obj):
    #     room_name = obj.room
    #     room_id = obj.room.id
    #     return {'id': room_id, 'name': room_name}




class LessonSerializer(DynamicFieldsModelSerializer):
    discipline_name = serializers.CharField(source='discipline.name', read_only=True)
    discipline_type = serializers.CharField(source='discipline.type')
    teacher_names = serializers.StringRelatedField(source='discipline.teachers', many=True)
    teacher_ids = serializers.PrimaryKeyRelatedField(source='discipline.teachers', many=True, read_only=True)
    group_names = serializers.StringRelatedField(source='groups', many=True)
    group_ids = serializers.PrimaryKeyRelatedField(source='groups', many=True, read_only=True)
    lessons = serializers.SerializerMethodField()
    lessons_in_schedule = serializers.SerializerMethodField()
    time_start = serializers.CharField(source='start_time')
    day = serializers.CharField(source='day_of_week')
    available_rooms = serializers.SerializerMethodField()
    # teacher_short_names = serializers.SerializerMethodField()
    timing = serializers.SerializerMethodField()
    russian_date = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'discipline_name', 'discipline_type',
                  'teacher_names', 'day', 'time_start', 'group_names',
                  'group_ids', 'teacher_ids', 'lessons', 'lessons_in_schedule',
                  'week', 'date', 'room', 'available_rooms', 'timing',
                  'russian_date', 'room_name']

    def get_day(self, obj):
        weekday_capitalized = obj.day_of_week.capitalize()
        return weekday_capitalized

    def get_room_name(self, obj):
        if obj.room is not None:
            return obj.room.name

    def get_russian_date(self, obj):
        months = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        str_date = f"{obj.date.day} {months[obj.date.month]}"
        return str_date

    def get_teacher_short_name(self, obj):
        teacher_names = obj.discipline.teacher.name
        clear_name = name = re.sub(r'\s?\([^)]*\)\s*', ' ', teacher_name).strip()
        list_from_clear_name = clear_name.split()
        short_name = f'{list_from_clear_name[0]} {list_from_clear_name[1][0]}.{list_from_clear_name[2][0]}.'
        return short_name

    def get_timing(self, obj):
        start, finish = obj.start_time, obj.finish_time

        timing = f"{start.strftime('%H:%M')} - {finish.strftime('%H:%M')}"
        return timing

    def get_lessons(self, obj):
        return round(obj.discipline.hours / 2)

    def get_lessons_in_schedule(self, obj):
        return Lesson.objects.filter(discipline=obj.discipline).count()

    def get_available_rooms(self, obj):
        """
        Возвращает список доступных комнат для данного урока,
        включая комнату текущего урока, если она уже назначена.
        """
        # Получаем занятые комнаты для указанного времени, исключая текущую комнату
        occupied_rooms = Lesson.objects.filter(
            date=obj.date,
            start_time=obj.start_time
        ).exclude(id=obj.id).exclude(room__type='Online').exclude(room_id=None).values_list('room_id')

        print(occupied_rooms)  # Выводим количество занятых комнат

        # Возвращаем комнаты, которые либо не заняты, либо имеют тип 'Online'
        available_rooms = Room.objects.all()
        # print(available_rooms)

        # print(f'{Room.objects.all().count()} всего')
        return [
            {
                "id": room.id,
                "name": room.name,
                "location": room.location,
                "size": room.size,
                "type": room.type,
            }
            for room in available_rooms
        ]


class TeacherLimitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherLimitation
        fields = ['id', 'day', 'time_start', 'time_finish', 'teacher']


class WeekSerializer(serializers.ModelSerializer):
    dates = serializers.SerializerMethodField()

    class Meta:
        model = Week
        fields = ['id', 'order_number', 'dates']

    def get_dates(self, obj):
        months = {
            1: "января", 2: "февраля", 3: "марта", 4: "апреля",
            5: "мая", 6: "июня", 7: "июля", 8: "августа",
            9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
        }
        str_date = f"{obj.start_date.day} {months[obj.start_date.month]} - " \
                   f"{obj.finish_date.day} {months[obj.finish_date.month]}"
        return str_date


class ActualUserSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['user_type', 'edu_group', 'teacher', 'id', 'group_name', 'teacher_name']

    def get_group_name(self, obj):
        if obj.edu_group:
            return obj.edu_group.name
        else:
            return None

    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.name
        else:
            return None

