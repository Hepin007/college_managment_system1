from datetime import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    CustomUser, Department, Student, Faculty, Subject, Timetable, Assignment, Submission,
    LeaveRequest, Feedback, Attendance, AttendanceReport,
    StudentResult, Fee
)

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput)
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'HOD'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)


# --------- User Creation Forms ---------
class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


# --------- Student Form ---------
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'roll_number', 'year','semester', 'contact_number',
            'gender', 'address', 'session_start', 'session_end'
        ]
        widgets = {
            'session_start': forms.DateInput(attrs={'type': 'date'}),
            'session_end': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'roll_number': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --------- Faculty Form ---------
class FacultyForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ['department', 'gender', 'address', 'contact_number', 'DOJ']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'DOJ': forms.DateInput(attrs={'type': 'date','required': True}),
        }

# --------- Attendace Form ---------
class AttendanceFilterForm(forms.Form):
    semester = forms.ChoiceField(
        choices=[(str(i), f"Semester {i}") for i in range(1, 9)],
        required=True,
        label="Select Semester"
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        label="Select Subject"
    )

    def __init__(self, *args, **kwargs):
        semester = kwargs.pop('semester', None)
        super().__init__(*args, **kwargs)
        if semester:
            self.fields['subject'].queryset = Subject.objects.filter(semester=int(semester))

  


# class AttendanceSubmissionForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         students = kwargs.pop('students', [])
#         super().__init__(*args, **kwargs)
#         for student in students:
#             self.fields[f'student_{student.id}'] = forms.ChoiceField(
#                 label=student.user.username,
#                 choices=[('present', 'Present'), ('absent', 'Absent')],
#                 widget=forms.RadioSelect
#             )


# class StudentAttendanceForm(forms.Form):
#     def __init__(self, *args, **kwargs):
#         students = kwargs.pop('students')
#         super(StudentAttendanceForm, self).__init__(*args, **kwargs)
        
#         for student in students:
#             self.fields[f'student_{student.id}'] = forms.ChoiceField(
#                 label=student.user.username,
#                 choices=[('present', 'Present'), ('absent', 'Absent')],
#                 widget=forms.RadioSelect,
#                 initial='Pending'
#             )


# ---------- Result Form ----------
class ResultReviewForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['status']


# --------- Timetable Form ---------
class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = '__all__'
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()


# class TimetableForm(forms.ModelForm):
#     class Meta:
#         model = Timetable
#         fields = '__all__'

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['subject'].queryset = Subject.objects.none()

#         if 'department' in self.data and 'semester' in self.data:
#             department_id = self.data.get('department')
#             semester = self.data.get('semester')
#             self.fields['subject'].queryset = Subject.objects.filter(
#                 department_id=department_id,
#                 semester=semester
#             )
#         elif self.instance.pk:
#             self.fields['subject'].queryset = Subject.objects.filter(
#                 department=self.instance.department,
#                 semester=self.instance.semester
#             )


# --------- Assignment Upload Form ---------
class SemesterForm(forms.Form):
    semester = forms.ChoiceField(
        choices=Assignment.SEMESTER_CHOICES,
        label="Select Semester",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'due_date', 'file']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

# --------- Submission Upload Form ---------
class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['assignment', 'file']

# --------- Leave Request Form ---------
class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date' , 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter reason for leave...'}),
            'start_date': forms.DateInput(attrs={'type': 'date','required': True}),
            'end_date': forms.DateInput(attrs={'type': 'date','required': True}),
        }
        labels = {
            'reason': 'Reason for Leave',
        }

# --------- Feedback Form ---------
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_text']

# --------- Attendance Marking Form ---------
class SemesterForm(forms.Form):
    SEMESTER_CHOICES = [(i, f'Semester {i}') for i in range(1, 9)]
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)

class SubjectForm(forms.Form):
    subject = forms.ModelChoiceField(queryset=Subject.objects.none())

    def __init__(self, faculty, semester, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.filter(faculty=faculty, semester=semester)

# --------- Grade Entry Form ---------
class SemesterForm(forms.Form):
    semester = forms.IntegerField(label="Select Semester", min_value=1, max_value=8)

class GradeEntryForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.none(), label="Student")
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), label="Subject")
    grade = forms.CharField(label="Grade", max_length=2)

    def __init__(self, faculty=None, semester=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if faculty and semester:
            self.fields['subject'].queryset = Subject.objects.filter(faculty=faculty, semester=semester)
            self.fields['student'].queryset = Student.objects.filter(semester=semester)

# --------- Fees Entry Form ---------
class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'semester', 'amount', 'status']



