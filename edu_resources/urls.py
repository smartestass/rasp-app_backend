from django.contrib import admin
from django.urls import path, include
from .views import *


urlpatterns = [
    # path('api/curricula/', CurriculumListView.as_view(), name='curriculum-list'),
    # path('api/discipline_nagruzka/<int:group_id>/<int:semester_id>/', get_discipline_nagruzka),
    # path('api/schedule_info/', GroupRowAPIView.as_view()),
    # path('api/lessonpatterns/<int:group_id>/<int:semester_id>/', LessonPatternAPIView.as_view()),
    path('group-selection/', group_selection_view, name='group_selection'),
    path('group-selection/', group_selection_view, name='index'),
    # # path('create-schedule/', choice_group_view, name='choice_group'),
    # path('create-schedule/<int:group_id>/', create_schedule_view, name='create_schedule'),
    # # path('create-schedule/<int:group_id>/<int:semester_id>/<int:disc_id>', create_schedule_view, name='create_pattern'),
    # path('schedule/group/<int:group_id>', schedule_view, {'schedule_type': 'group'}, name='schedule_group'),
    path('limitation/', teacher_limitations_view, name='limitation'),
    path('edit-schedule/<int:group_id>/', edit_real_schedule, name='edit_real_schedule'),
    path('schedule_new/group', schedule_view_new, {'schedule_type': 'group'}, name='schedule_group_new'),
    path('schedule_new/teacher', schedule_view_new, {'schedule_type': 'teacher'}, name='schedule_teacher_new'),
    # path('token_details', token_details, name='token_details'),
    path('role/', role_choosing, name='role_choosing'),
    path('rasp/group', view_schedule, {'schedule_type': 'group'}, name='rasp_group'),
    path('rasp/teacher', view_schedule, {'schedule_type': 'teacher'}, name='rasp_teacher'),
    path('', redirect_to_schedule, name='home'),
    path('create/', create_teacher_users),
    path('api/user_details/<str:email>', user_details, name='user_details'),
    path('api/search/<str:model>/<str:search_string>', search, name='search'),
    path('api/<str:rasp_type>/<int:id>', get_week_lessons, name='lessons'),
    path('api/dates/<str:rasp_type>/<int:id>', get_dates_with_lessons, name='dates_with_lessons'),
    path('create_students/', create_student_users),
]
