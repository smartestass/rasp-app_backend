import os
import django
from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule_creator.settings")
django.setup()

from edu_resources.models import EduGroup, TeacherFromHand, LessonFromHand

teachers = TeacherFromHand.objects.all()

overlapping_lessons = LessonFromHand.objects.values(
    'group__name', 'date', 'start_time'
).annotate(
    num_lessons=Count('id')
).filter(num_lessons__gt=1)


overlapping_details = []

for overlap in overlapping_lessons:
    group_name = overlap['group__name']
    if group_name in ['21ПП-37.03.01.01-о2', '21ПП-37.03.01.01-о1']:
        continue
    date = overlap['date']
    time = overlap['start_time']

    # Находим все занятия для этой группы, даты и времени
    lessons = LessonFromHand.objects.filter(
        group__name=group_name,
        date=date,
        start_time=time
    ).select_related().prefetch_related('teachers', 'group')

    # Добавляем информацию о пересекающихся занятиях
    overlapping_details.append({
        'group': group_name,
        'date': date,
        'time': time,
        'lessons': [
            {
                'id': lesson.id,
                'title': lesson.discipline,
                'teachers': [teacher.shortname for teacher in lesson.teachers.all()]
            }
            for lesson in lessons
        ]
    })

[print(i) for i in overlapping_details]

# for lesson in overlapping_lessons:
#     print(f'Накладка для группы {lesson["group__name"]} на {lesson["date"]} в {lesson["start_time"]}')