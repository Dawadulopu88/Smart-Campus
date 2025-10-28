from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path(
        "notification/mark-as-read/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path("notification/clear-all/", views.clear_all_notification, name="clear_all_notification"),
    # Teacher URLs
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/add/", views.add_teacher, name="add_teacher"),
    path("teachers/edit/<int:pk>/", views.edit_teacher, name="edit_teacher"),
    path("teachers/delete/<int:pk>/", views.delete_teacher, name="delete_teacher"),
    path("teacher-dashboard.html", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacherlist.html", views.teacher_list_page, name="teacher_list_page"),
    path("teacher-details.html/<int:pk>/", views.teacher_details, name="teacher_details"),
    # Student Dashboard URLs
    path("student-dashboard/", views.student_dashboard, name="student_dashboard"),
    path("student-dashboard.html", views.student_dashboard, name="student_dashboard_html"),
    # Department URLs
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.add_department, name="add_department"),
    path("departments/edit/<int:pk>/", views.edit_department, name="edit_department"),
    path("departments/delete/<int:pk>/", views.delete_department, name="delete_department"),
    path("departments/detail/<int:pk>/", views.department_detail, name="department_detail"),
    # Subject URLs
    path("subjects/", views.subject_list, name="subject_list"),
    path("subjects/add/", views.add_subject, name="add_subject"),
    path("subjects/edit/<int:pk>/", views.edit_subject, name="edit_subject"),
    path("subjects/delete/<int:pk>/", views.delete_subject, name="delete_subject"),
    # Holiday URLs
    path("holiday.html", views.holiday_list, name="holiday_list"),
    path("holidays/", views.holiday_list, name="holidays"),
    path("holidays/add/", views.add_holiday, name="add_holiday"),
    path("holidays/edit/<int:pk>/", views.edit_holiday, name="edit_holiday"),
    path("holidays/delete/<int:pk>/", views.delete_holiday, name="delete_holiday"),
    # Fees URLs
    path("fees.html", views.fees_list, name="fees_list"),
    path("fees/", views.fees_list, name="fees"),
    # Exam URLs
    path("exam.html", views.exam_list, name="exam_list"),
    path("exams/", views.exam_list, name="exams"),
    # Events URLs
    path("event.html", views.events_list, name="events_list"),
    path("events/", views.events_list, name="events"),
    # Time Table URLs
    path("time-table.html", views.time_table, name="time_table"),
    path("timetable/", views.time_table, name="timetable"),
    # Library URLs
    path("library.html", views.library, name="library"),
    path("library/", views.library, name="library_management"),
    # Hostel URLs
    path("hostel.html", views.hostel, name="hostel"),
    path("hostel/", views.hostel, name="hostel_management"),
    # Transport URLs
    path("transport.html", views.transport, name="transport"),
    path("transport/", views.transport, name="transport_management"),
    # Sports URLs
    path("sports.html", views.sports, name="sports"),
    path("sports/", views.sports, name="sports_management"),
    # Inbox URLs
    path("inbox/", views.inbox, name="inbox"),
    path("inbox.html", views.inbox, name="inbox_html"),
    # Other URLs
    path(
        "student-dashboard.html",
        lambda request: render(request, "Home/index.html", {"welcome_user": "students"}),
        name="student_dashboard",
    ),
    path("profile.html", views.profile_view, name="profile"),
    path("user-profiles.html", views.user_profiles_view, name="user_profiles"),
]
