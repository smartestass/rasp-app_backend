import django
import os
from openpyxl import load_workbook
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule_creator.settings")
django.setup()
from edu_resources.models import Semester, Discipline, Week, EduGroup


days_to_append = 0
weeks = 0
# semester = SemesterCurrent.objects.filter(curriculum__groups=group).get(start_date=date(2025, 2, 3))
start_date = date(2025, 2, 3)
finish_date = start_date + timedelta(days=6)
while weeks != 21:
    weeks += 1
    Week.objects.create(
                        start_date=start_date + timedelta(days=days_to_append),
                        finish_date=finish_date + timedelta(days=days_to_append),
                        order_number=weeks)
    days_to_append += 7


