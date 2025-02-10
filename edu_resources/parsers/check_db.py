import django
import os
from openpyxl import load_workbook
import pandas as pd
from django.db.models import Count

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule_creator.settings")
django.setup()

from edu_resources.models import Teacher, Discipline, EduGroup


group1 = EduGroup.objects.get(name='22ПП-37.05.01.01-о1')
group2 = EduGroup.objects.get(name='22ПП-37.05.01.01-о2')

d = Discipline.objects.get(pk=12715).groups.exclude(name='24ПП-37.05.01.01-о1')
print(d)