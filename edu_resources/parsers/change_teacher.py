import os
import django
from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule_creator.settings")
django.setup()

from edu_resources.models import EduGroup, TeacherFromHand, LessonFromHand


teachers = TeacherFromHand.objects.filter(name__istartswith='Проненко')

lessons = LessonFromHand.objects.filter(teachers=25)
for l in lessons:
    l.teachers.remove(25)
    l.teachers.add(28)

print(LessonFromHand.objects.filter(teachers=25))