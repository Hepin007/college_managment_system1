from django.db import models
from django.contrib.auth.models import AbstractUser

# # Custom user with role types
# class CustomUser(AbstractUser):
#     USER_TYPE_CHOICES = (
#         (1, "HOD"),
#         (2, "Faculty"),
#         (3, "Student"),
#     )
#     user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)

# Department model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    faculty = models.ForeignKey("Faculty", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

# Timetable
class Timetable(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    day = models.CharField(max_length=20)
    time = models.TimeField()

    def __str__(self):
        return f"{self.subject.name} - {self.day} - {self.time}"

# # faculty
# class Faculty(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
#     address = models.TextField()

#     def __str__(self):
#         return self.user.username

# # student
# class Student(models.Model):
#     user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
#     department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
#     gender = models.CharField(max_length=10)
#     address = models.TextField()

#     def __str__(self):
#         return self.user.username

# attendance
class Attendance(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

class AttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)  # True = Present, False = Absent

# result
class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)  # A, B, C, etc.


# apply leave
class LeaveRequest(models.Model):
    USER_TYPE_CHOICES = (
        ('Faculty', 'Faculty'),
        ('Student', 'Student'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=(('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')), default='Pending')
    date = models.DateField(auto_now_add=True)

# assignment (faculty)
class Assignment(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/')


# submisson (faculty)
class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    approved = models.BooleanField(default=False)
    submitted_on = models.DateTimeField(auto_now_add=True)

# fees
class Fee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=(('Paid', 'Paid'), ('Unpaid', 'Unpaid')))


# feedback
class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)
