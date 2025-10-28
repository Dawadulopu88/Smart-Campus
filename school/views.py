from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from functools import wraps
from django import forms
from .models import Notification, Teacher, Department, Holiday, Subject


def teacher_details(request, pk):
    teachers = Teacher.objects.all()
    selected = teachers.filter(pk=pk).first()
    return render(
        request,
        "teacher-details.html",
        {
            "teacher": selected,  # backward compatibility
            "selected_teacher": selected,
            "teachers": teachers,
        },
    )


def teacher_list_page(request):
    from .models import Teacher

    teachers = Teacher.objects.all()
    return render(request, "teacherlist.html", {"teachers": teachers})


"""Views for school app (teachers, dashboard, profiles, notifications)."""


# Teacher Form
class TeacherForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label="First Name")
    last_name = forms.CharField(max_length=100, required=True, label="Last Name")

    class Meta:
        model = Teacher
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "gender",
            "date_of_birth",
            "address",
            "joining_date",
            "teacher_image",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
        }


# List Teachers
def teacher_list(request):
    teachers = Teacher.objects.all()
    return render(request, "teachers.html", {"teachers": teachers})


# Add Teacher
def add_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("teacher_list")
    else:
        form = TeacherForm()
    return render(request, "add-teacher.html", {"form": form})


# Edit Teacher
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect("teacher_list")
    else:
        form = TeacherForm(instance=teacher)
    return render(request, "edit-teacher.html", {"form": form, "teacher": teacher})


# Delete Teacher
def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        teacher.delete()
        return redirect("teacher_list")
    return render(request, "delete-teacher.html", {"teacher": teacher})


# Create your views here.


def teacher_dashboard(request):
    # Ensure only teachers can access teacher dashboard
    if not request.user.is_authenticated:
        return redirect("login")

    if not (hasattr(request.user, "is_teacher") and request.user.is_teacher):
        messages.error(request, "Access denied. Teachers only.")
        return redirect("index")

    from .models import Teacher

    teachers = Teacher.objects.all()
    return render(
        request, "Home/teacher-dashboard.html", {"welcome_user": "Teacher", "teachers": teachers}
    )


def index(request):
    if not request.user.is_authenticated:
        return render(request, "authentication/login.html")

    # Redirect to appropriate dashboard based on user role
    if hasattr(request.user, "is_admin") and request.user.is_admin:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Get all students for display
        students = User.objects.filter(is_student=True).order_by("first_name", "last_name")

        context = {
            "welcome_user": "Admin",
            "students": students,
            "total_students": students.count(),
        }
        return render(request, "Home/index.html", context)
    elif hasattr(request.user, "is_teacher") and request.user.is_teacher:
        return redirect("teacher_dashboard")  # Redirect teachers to their dashboard
    elif hasattr(request.user, "is_student") and request.user.is_student:
        return redirect("student_dashboard")  # Redirect students to their dashboard
    else:
        return render(request, "authentication/login.html")


def dashboard(request):
    # student dashboard placeholder (notifications already surfaced elsewhere if needed)
    return render(request, "students/student-dashboard.html")


def student_dashboard(request):
    # Ensure only students can access student dashboard
    if not request.user.is_authenticated:
        return redirect("login")

    if not (hasattr(request.user, "is_student") and request.user.is_student):
        messages.error(request, "Access denied. Students only.")
        return redirect("index")

    context = {"welcome_user": "Student", "title": "Student Dashboard"}
    return render(request, "student-dashboard.html", context)


def mark_notification_as_read(request):
    if request.method == "POST":
        notification = Notification.objects.filter(user=request.user, is_read=False)
        notification.update(is_read=True)
        return JsonResponse({"status": "success"})
    return HttpResponseForbidden()


def clear_all_notification(request):
    if request.method == "POST":
        notification = Notification.objects.filter(user=request.user)
        notification.delete()
        return JsonResponse({"status": "success"})
    return HttpResponseForbidden


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect("index")

    # Determine user role for profile customization
    user_role = "User"
    if hasattr(request.user, "is_admin") and request.user.is_admin:
        user_role = "Admin"
    elif hasattr(request.user, "is_teacher") and request.user.is_teacher:
        user_role = "Teacher"
    elif hasattr(request.user, "is_student") and request.user.is_student:
        user_role = "Student"

    context = {"user_role": user_role, "user": request.user}

    return render(request, "profile.html", context)


def user_profiles_view(request):
    """View to display all registered user profiles"""
    if not request.user.is_authenticated:
        return redirect("index")

    from home_auth.models import CustomUser

    # Get all users with their profile information
    all_users = CustomUser.objects.all().order_by("-date_joined")

    context = {
        "all_users": all_users,
        "total_users": all_users.count(),
        "total_students": all_users.filter(is_student=True).count(),
        "total_teachers": all_users.filter(is_teacher=True).count(),
        "total_admins": all_users.filter(is_admin=True).count(),
    }

    return render(request, "user-profiles.html", context)


# Admin decorator to restrict access to admin users only
def admin_required(function):
    @wraps(function)
    @login_required
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, "is_admin") or not request.user.is_admin:
            messages.error(request, "You don't have permission to access this page.")
            raise PermissionDenied("Admin access required")
        return function(request, *args, **kwargs)

    return wrap


# Department Form
class DepartmentForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True, label="Department Name")
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Enter department description..."}),
        required=False,
        label="Description",
    )

    class Meta:
        model = Department
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter department name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter department description...",
                    "rows": 4,
                }
            ),
        }


# Department Views


# List Departments (accessible to all authenticated users)
@login_required
def department_list(request):
    departments = Department.objects.all().order_by("name")
    context = {
        "departments": departments,
        "total_departments": departments.count(),
        "user_is_admin": hasattr(request.user, "is_admin") and request.user.is_admin,
    }
    return render(request, "departments/department_list.html", context)


# Add Department (admin only)
@admin_required
def add_department(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Department '{form.cleaned_data['name']}' has been added successfully!"
            )
            return redirect("department_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm()

    context = {"form": form, "title": "Add New Department"}
    return render(request, "departments/add_department.html", context)


# Edit Department (admin only)
@admin_required
def edit_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == "POST":
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Department '{form.cleaned_data['name']}' has been updated successfully!"
            )
            return redirect("department_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DepartmentForm(instance=department)

    context = {
        "form": form,
        "department": department,
        "title": f"Edit Department: {department.name}",
    }
    return render(request, "departments/edit_department.html", context)


# Delete Department (admin only)
@admin_required
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        department_name = department.name
        try:
            department.delete()
            messages.success(
                request, f"Department '{department_name}' has been deleted successfully!"
            )
        except Exception as e:
            messages.error(request, f"Error deleting department: {str(e)}")
        return redirect("department_list")

    # Check if department has any subjects
    subject_count = department.subject_set.count() if hasattr(department, "subject_set") else 0

    context = {
        "department": department,
        "subject_count": subject_count,
        "title": f"Delete Department: {department.name}",
    }
    return render(request, "departments/delete_department.html", context)


# Department Detail View (accessible to all authenticated users)
@login_required
def department_detail(request, pk):
    department = get_object_or_404(Department, pk=pk)
    subjects = department.subject_set.all() if hasattr(department, "subject_set") else []

    context = {
        "department": department,
        "subjects": subjects,
        "user_is_admin": hasattr(request.user, "is_admin") and request.user.is_admin,
    }
    return render(request, "departments/department_detail.html", context)


# Holiday Form
class HolidayForm(forms.ModelForm):
    name = forms.CharField(max_length=200, required=True, label="Holiday Name")
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Holiday Date",
    )
    holiday_type = forms.ChoiceField(
        choices=Holiday.HOLIDAY_TYPES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Holiday Type",
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Enter holiday description..."}),
        required=False,
        label="Description",
    )
    is_recurring = forms.BooleanField(
        required=False,
        label="Recurring Holiday",
        help_text="Check if this holiday occurs every year",
    )

    class Meta:
        model = Holiday
        fields = ["name", "date", "holiday_type", "description", "is_recurring"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter holiday name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter holiday description...",
                    "rows": 4,
                }
            ),
        }


# Holiday Views


# List Holidays (accessible to all authenticated users)
@login_required
def holiday_list(request):
    current_year = timezone.now().year
    year = request.GET.get("year", current_year)

    try:
        year = int(year)
    except (ValueError, TypeError):
        year = current_year

    # Get holidays for the specified year
    holidays = Holiday.objects.filter(date__year=year, is_active=True).order_by("date")

    # Get upcoming holidays
    upcoming_holidays = Holiday.objects.filter(
        date__gte=timezone.now().date(), is_active=True
    ).order_by("date")[:5]

    # Group holidays by month
    holidays_by_month = {}
    for holiday in holidays:
        month = holiday.date.strftime("%B")
        if month not in holidays_by_month:
            holidays_by_month[month] = []
        holidays_by_month[month].append(holiday)

    # Get holiday statistics
    total_holidays = holidays.count()
    holiday_type_counts = {
        "national": holidays.filter(holiday_type="national").count(),
        "religious": holidays.filter(holiday_type="religious").count(),
        "international": holidays.filter(holiday_type="international").count(),
        "special": holidays.filter(holiday_type="special").count(),
        "bank": holidays.filter(holiday_type="bank").count(),
    }

    context = {
        "holidays": holidays,
        "holidays_by_month": holidays_by_month,
        "upcoming_holidays": upcoming_holidays,
        "current_year": year,
        "total_holidays": total_holidays,
        "holiday_type_counts": holiday_type_counts,
        "user_is_admin": hasattr(request.user, "is_admin") and request.user.is_admin,
        "available_years": range(current_year - 2, current_year + 3),
    }
    return render(request, "holiday.html", context)


# Add Holiday (admin only)
@admin_required
def add_holiday(request):
    if request.method == "POST":
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Holiday '{form.cleaned_data['name']}' has been added successfully!"
            )
            return redirect("holiday_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HolidayForm()

    context = {"form": form, "title": "Add New Holiday"}
    return render(request, "holidays/add_holiday.html", context)


# Edit Holiday (admin only)
@admin_required
def edit_holiday(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == "POST":
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Holiday '{form.cleaned_data['name']}' has been updated successfully!"
            )
            return redirect("holiday_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = HolidayForm(instance=holiday)

    context = {"form": form, "holiday": holiday, "title": f"Edit Holiday: {holiday.name}"}
    return render(request, "holidays/edit_holiday.html", context)


# Delete Holiday (admin only)
@admin_required
def delete_holiday(request, pk):
    holiday = get_object_or_404(Holiday, pk=pk)

    if request.method == "POST":
        holiday_name = holiday.name
        try:
            holiday.delete()
            messages.success(request, f"Holiday '{holiday_name}' has been deleted successfully!")
        except Exception as e:
            messages.error(request, f"Error deleting holiday: {str(e)}")
        return redirect("holiday_list")

    context = {"holiday": holiday, "title": f"Delete Holiday: {holiday.name}"}
    return render(request, "holidays/delete_holiday.html", context)


# Fees view
def fees_list(request):
    """Display fees management page"""
    context = {"title": "Fees Management", "page_title": "Fees Management System"}
    return render(request, "fees.html", context)


# Exam List view
def exam_list(request):
    """Display exam list page"""
    context = {"title": "Exam List", "page_title": "Examination Management"}
    return render(request, "exam_list.html", context)


# Events view
def events_list(request):
    """Display events page"""
    context = {"title": "Events", "page_title": "Campus Events"}
    return render(request, "events.html", context)


# Time Table view
def time_table(request):
    """Display time table page"""
    context = {"title": "Time Table", "page_title": "Class Schedule"}
    return render(request, "time_table.html", context)


# Library view
def library(request):
    """Display library page"""
    context = {"title": "Library", "page_title": "Library Management"}
    return render(request, "library.html", context)


# Hostel view
def hostel(request):
    """Display hostel page"""
    context = {"title": "Hostel Management", "page_title": "Student Accommodation"}
    return render(request, "hostel.html", context)


# Transport view
def transport(request):
    """Display transport page"""
    context = {"title": "Transport Management", "page_title": "School Transportation"}
    return render(request, "transport.html", context)


# Sports view
def sports(request):
    """Display sports page"""
    context = {"title": "Sports Management", "page_title": "Sports Activities"}
    return render(request, "sports.html", context)


# Inbox view
@login_required
def inbox(request):
    """Display inbox page for messaging system"""
    from django.contrib.auth import get_user_model
    from .models import Teacher

    User = get_user_model()

    # Get real users from database
    admins = User.objects.filter(is_admin=True)[:2]
    teachers = Teacher.objects.all()[:3]  # Using Teacher model for more details
    students = User.objects.filter(is_student=True)[:2]

    # Prepare sample messages with real users
    sample_messages = []

    # Add admin messages
    for admin in admins:
        sample_messages.append(
            {
                "sender": admin,
                "sender_type": "Administrator",
                "subject": "New Academic Year Guidelines",
                "content": "Please review the updated guidelines for the new academic year. Important changes have been made to the curriculum...",
                "time": "2 hrs ago",
                "is_unread": True,
                "is_starred": False,
            }
        )

    # Add teacher messages
    for teacher in teachers:
        sample_messages.append(
            {
                "sender": teacher,
                "sender_type": "Teacher",
                "subject": "Meeting Schedule Update",
                "content": "The weekly staff meeting has been rescheduled to Thursday at 3:00 PM. Please update your calendars accordingly.",
                "time": "5 hrs ago",
                "is_unread": False,
                "is_starred": True,
            }
        )
        break  # Only show one teacher message for demo

    # Add student messages
    for student in students:
        sample_messages.append(
            {
                "sender": student,
                "sender_type": "Student",
                "subject": "Assignment Submission Query",
                "content": "I have a question about the submission deadline for the Mathematics assignment. Could you please clarify...",
                "time": "1 day ago",
                "is_unread": True,
                "is_starred": False,
            }
        )
        break  # Only show one student message for demo

    context = {
        "title": "Inbox",
        "page_title": "Message Center",
        "sample_messages": sample_messages,
        "user_role": "Administrator"
        if hasattr(request.user, "is_admin") and request.user.is_admin
        else "Teacher"
        if hasattr(request.user, "is_teacher") and request.user.is_teacher
        else "Student"
        if hasattr(request.user, "is_student") and request.user.is_student
        else "User",
    }
    return render(request, "inbox.html", context)


# Subject Management Views


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code", "department"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter subject name"}
            ),
            "code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter subject code"}
            ),
            "department": forms.Select(attrs={"class": "form-control"}),
        }


def role_required(*allowed_roles):
    """Decorator to check if user has required role"""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            user_roles = []
            if hasattr(request.user, "is_admin") and request.user.is_admin:
                user_roles.append("admin")
            if hasattr(request.user, "is_teacher") and request.user.is_teacher:
                user_roles.append("teacher")
            if hasattr(request.user, "is_student") and request.user.is_student:
                user_roles.append("student")

            if any(role in allowed_roles for role in user_roles):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return wrapper

    return decorator


@login_required
@role_required("admin", "teacher", "student")
def subject_list(request):
    """List all subjects - accessible to all roles"""
    subjects = Subject.objects.select_related("department").all()

    # Calculate unique department count
    department_count = subjects.values("department").distinct().count()

    # More robust role detection
    is_admin = hasattr(request.user, "is_admin") and request.user.is_admin
    is_teacher = hasattr(request.user, "is_teacher") and request.user.is_teacher
    is_student = hasattr(request.user, "is_student") and request.user.is_student

    context = {
        "subjects": subjects,
        "title": "Subject List",
        "can_add": is_admin or is_teacher,
        "can_edit": is_admin or is_teacher,
        "can_delete": is_admin or is_teacher,
        "department_count": department_count,
        "user_role": "admin"
        if is_admin
        else "teacher"
        if is_teacher
        else "student"
        if is_student
        else "user",
    }
    return render(request, "subjects/subject_list.html", context)


@login_required
@role_required("admin", "teacher")
def add_subject(request):
    """Add new subject - only admin and teachers"""
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject added successfully!")
            return redirect("subject_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SubjectForm()

    context = {"form": form, "title": "Add Subject", "action": "Add"}
    return render(request, "subjects/subject_form.html", context)


@login_required
@role_required("admin", "teacher")
def edit_subject(request, pk):
    """Edit subject - only admin and teachers"""
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == "POST":
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, "Subject updated successfully!")
            return redirect("subject_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SubjectForm(instance=subject)

    context = {"form": form, "subject": subject, "title": "Edit Subject", "action": "Edit"}
    return render(request, "subjects/subject_form.html", context)


@login_required
@role_required("admin", "teacher")
def delete_subject(request, pk):
    """Delete subject - only admin and teachers"""
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == "POST":
        subject.delete()
        messages.success(request, "Subject deleted successfully!")
        return redirect("subject_list")

    context = {"subject": subject, "title": "Delete Subject"}
    return render(request, "subjects/subject_delete.html", context)
