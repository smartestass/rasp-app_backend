from django.contrib import admin

# from .models import Curriculum, Teacher, Discipline, EduGroup, Semester, DisciplinePart, DisciplineNagruzka
# from .models import RoomType, Room, DisciplineType, Location, SemesterCurrent
#
#
# # Register your models here.
#
# @admin.register(SemesterCurrent)
# class SemesterCurrentAdmin(admin.ModelAdmin):
#     list_display = ('semester', 'curriculum', 'start_date')
#
#
# @admin.register(DisciplineNagruzka)
# class NagruzkaAdmin(admin.ModelAdmin):
#     list_display = ('discipline_part', 'teacher', 'hours')
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == 'discipline_part':
#             kwargs['queryset'] = DisciplinePart.objects.filter(semester__start_date__year=2025)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
#
#
# # @admin.register(Curriculum)
# # class CurriculumAdmin(admin.ModelAdmin):
# #     list_display = ('name', 'start_date')
# #     search_fields = ('name', )
#
#
# @admin.register(Teacher)
# class TeacherAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     search_fields = list_display
#
#
# # @admin.register(EduGroup)
# # class EduGroupAdmin(admin.ModelAdmin):
# #     list_display = ('name', 'size', 'curriculum')
# #     search_fields = ('name', )
#
#
# @admin.register(Discipline)
# class DisciplineAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     search_fields = list_display
#
#
# @admin.register(DisciplinePart)
# class DisciplinePartAdmin(admin.ModelAdmin):
#     list_display = ('discipline', 'type', 'hours')
#
#
# @admin.register(Semester)
# class SemesterAdmin(admin.ModelAdmin):
#     list_display = ('number', )
#     search_fields = list_display
#
#
# @admin.register(DisciplineType)
# class DisciplineTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     search_fields = list_display
#
#
# @admin.register(RoomType)
# class RoomTypeAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     search_fields = list_display
#
#
# @admin.register(Room)
# class RoomAdmin(admin.ModelAdmin):
#     list_display = ('location', 'name', 'size', 'type')
#     search_fields = ('name', )
#
#
# @admin.register(Location)
# class LocationAdmin(admin.ModelAdmin):
#     list_display = ('name', )
#     search_fields = list_display
