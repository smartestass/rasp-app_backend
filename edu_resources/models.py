from django.db import models
from django.contrib.auth.models import AbstractUser


# Учебная группа
class EduGroup(models.Model):
    name = models.CharField(max_length=30)
    work_plan = models.CharField(max_length=15, null=True)
    form = models.CharField(max_length=20, null=True)
    course = models.IntegerField(null=True)
    naprav = models.CharField(max_length=100, null=True)
    profile = models.CharField(max_length=150, null=True)
    email = models.EmailField(null=True)
    size = models.IntegerField(null=True)
    ms_id = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"


# Преподаватель
class Teacher(models.Model):
    name = models.CharField(max_length=100)
    kafedra = models.CharField(max_length=150)
    stepen = models.CharField(max_length=100, null=True)
    zvanie = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return f"{self.name}"



# Аудитория
class Room(models.Model):
    location = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    size = models.IntegerField(null=True)
    type = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.size})"


class Semester(models.Model):
    number = models.FloatField()
    name = models.CharField(max_length=20)

    def __str__(self):
        return f"Семестр {self.number}"


# # Семестр конкретной группы
# class SemesterCurrent(models.Model):
#     semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
#     curriculum = models.ForeignKey(Curriculum, related_name='semesters', on_delete=models.CASCADE, null=True)
#     start_date = models.DateField(null=True)
#     finish_date = models.DateField(null=True)


# Дисциплина
class Discipline(models.Model):
    name = models.CharField(max_length=150)
    semester = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    hours = models.FloatField(null=True)
    kafedra = models.CharField(max_length=100)
    myam = models.CharField(max_length=3)
    groups = models.ManyToManyField(EduGroup)
    teachers = models.ManyToManyField(Teacher)

    def __str__(self):
        return f"{self.type}, {self.name}, {self.hours}"


#
# class DisciplineNagruzka(models.Model):
#     discipline_part = models.ForeignKey(DisciplinePart, on_delete=models.CASCADE)
#     teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
#     hours = models.IntegerField(null=True)


class LessonPattern(models.Model):
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    day = models.CharField(max_length=13)
    time_start = models.TimeField(auto_now=False, auto_now_add=False)
    time_finish = models.TimeField(auto_now=False, auto_now_add=False)


class Week(models.Model):
    # group = models.ForeignKey(EduGroup, on_delete=models.CASCADE, null=True)
    order_number = models.IntegerField(null=True)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    finish_date = models.DateField()


class Lesson(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, null=True)
    day_of_week = models.CharField(max_length=13, null=True)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    start_time = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    finish_time = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    groups = models.ManyToManyField(EduGroup)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)


class TeacherLimitation(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day = models.CharField(max_length=13)
    time_start = models.TimeField(auto_now=False, auto_now_add=False)
    time_finish = models.TimeField(auto_now=False, auto_now_add=False)


class LessonsFrom1c(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, null=True)
    day_of_week = models.CharField(max_length=13, null=True)
    discipline = models.CharField(max_length=100, null=True)
    teachers = models.ManyToManyField(Teacher)
    groups = models.ManyToManyField(EduGroup)
    date = models.DateField()
    start_time = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    finish_time = models.TimeField(auto_now=False, auto_now_add=False, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)


class TeacherFromHand(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']


class LessonFromHand(models.Model):
    discipline = models.CharField(max_length=250)
    teachers = models.ManyToManyField(TeacherFromHand)
    groups = models.ManyToManyField(EduGroup)
    date = models.DateField()
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    finish_time = models.TimeField(auto_now=False, auto_now_add=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    lesson_type = models.CharField(max_length=4)
    file_name = models.CharField(max_length=70, null=True)

    class Meta:
        ordering = ['date', 'start_time']


# Кастомная модель пользователя
class User(AbstractUser):
    user_type = models.CharField(max_length=10, null=True)
    edu_group = models.ForeignKey(EduGroup, on_delete=models.CASCADE, null=True)
    teacher = models.ForeignKey(TeacherFromHand, on_delete=models.CASCADE, null=True)
    short_name = models.CharField(max_length=20, null=True)
