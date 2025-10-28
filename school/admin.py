from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Notification)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "subject_count"]
    list_filter = ["name"]
    search_fields = ["name", "description"]
    ordering = ["name"]

    def subject_count(self, obj):
        return obj.subject_set.count()

    subject_count.short_description = "Number of Subjects"


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "email", "mobile", "gender", "joining_date"]
    list_filter = ["gender", "joining_date"]
    search_fields = ["first_name", "last_name", "email", "mobile"]
    ordering = ["first_name", "last_name"]
    date_hierarchy = "joining_date"


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "department"]
    list_filter = ["department"]
    search_fields = ["name", "code", "department__name"]
    ordering = ["department", "name"]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "holiday_type", "is_recurring", "is_active"]
    list_filter = ["holiday_type", "is_recurring", "is_active", "date"]
    search_fields = ["name", "description"]
    ordering = ["date"]
    date_hierarchy = "date"
    list_editable = ["is_active"]

    fieldsets = (
        ("Holiday Information", {"fields": ("name", "date", "holiday_type", "description")}),
        ("Settings", {"fields": ("is_recurring", "is_active"), "classes": ("collapse",)}),
    )
