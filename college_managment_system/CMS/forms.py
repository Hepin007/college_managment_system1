from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    CustomUser, Student, Faculty, Timetable, Assignment, Submission,
    LeaveRequest, Feedback, Attendance, AttendanceReport,
    StudentResult, Fee
)

# --------- User Creation Forms ---------
class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'user_type']


# --------- Student Form ---------
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['user', 'department', 'gender', 'address', 'session_start', 'session_end']

# --------- Faculty Form ---------
class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['user', 'department', 'gender', 'address']

# --------- Timetable Form ---------
class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['subject', 'faculty', 'department', 'day', 'time']

# --------- Assignment Upload Form ---------
class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'faculty', 'title', 'description', 'due_date', 'file']

# --------- Submission Upload Form ---------
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['assignment', 'file']

# --------- Leave Request Form ---------
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['reason']

# --------- Feedback Form ---------
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']

# --------- Attendance Marking Form ---------
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['subject', 'faculty', 'date']

class AttendanceReportForm(forms.ModelForm):
    class Meta:
        model = AttendanceReport
        fields = ['student', 'attendance', 'status']

# --------- Grade Entry Form ---------
class ResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['student', 'subject', 'grade']

# --------- Fees Entry Form ---------
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'semester', 'amount', 'status']
