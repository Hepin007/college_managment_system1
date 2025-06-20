from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_ROLES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('hod', 'HOD'),
    )
    user_type = models.CharField(max_length=10, choices=USER_ROLES, default='student')
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=USER_ROLES)
    

    def __str__(self):
        return f"{self.username}"

# Department model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# HOD Model
class HOD(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"HOD: {self.user.username}"

# Faculty Model
class Faculty(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=15,unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES) 
    address = models.TextField()
    DOJ = models.DateField() 
    
    @property
    def experience(self):
        if self.DOJ:
            today = date.today()
            return today.year - self.DOJ.year - ((today.month, today.day) < (self.DOJ.month, self.DOJ.day))
        return 0

    def __str__(self):
        return f"{self.user.username}"

# Student Model
class Student(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    SEMESTER_CHOICES = (
        ('Semester 1', 'Semester 1'),
        ('Semester 2', 'Semester 2'),
        ('Semester 3', 'Semester 3'),
        ('Semester 4', 'Semester 4'),
        ('Semester 5', 'Semester 5'),
        ('Semester 6', 'Semester 6'),
        ('Semester 7', 'Semester 7'),
        ('Semester 8', 'Semester 8'),
    )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15,unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES) 
    address = models.TextField()            
    session_start = models.DateField()      
    session_end = models.DateField()  

    class Meta:
        unique_together = ('roll_number', 'year')

    def __str__(self):
        return f"{self.user.username}"

# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True)
    # semester = models.CharField(max_length=10)
    semester = models.IntegerField()
    
    def __str__(self):
        return self.name

# Timetable
class Timetable(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    )
    SEMESTER_CHOICES = (
        ('Semester 1', 'Semester 1'),
        ('Semester 2', 'Semester 2'),
        ('Semester 3', 'Semester 3'),
        ('Semester 4', 'Semester 4'),
        ('Semester 5', 'Semester 5'),
        ('Semester 6', 'Semester 6'),
        ('Semester 7', 'Semester 7'),
        ('Semester 8', 'Semester 8'),
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20,choices=SEMESTER_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    

    def __str__(self):
        return f"{self.subject.name} - {self.day} - {self.start_time} - {self.end_time}"


# attendance
class Attendance(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

class AttendanceReport(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.BooleanField(default="pending", choices=STATUS_CHOICES)

# class AttendanceReport(models.Model):
#     STATUS_CHOICES = (
#         (True, 'Present'),
#         (False, 'Absent'),
#     )
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
#     status = models.BooleanField(choices=STATUS_CHOICES, default=True)


# result
class StudentResult(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Rejected', 'Rejected'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    grade = models.CharField(max_length=2)  # A, B, C, etc.
    semester = models.IntegerField()
    reviewed_by_HOD = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')


# apply leave
# class LeaveRequest(models.Model):
#     USER_TYPE_CHOICES = (
#         ('Faculty', 'Faculty'),
#         ('Student', 'Student'),
#     )
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
#     reason = models.TextField()
#     status = models.CharField(max_length=10, choices=(('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')), default='Pending')
#     date = models.DateField(auto_now_add=True)

class LeaveRequest(models.Model):
    USER_TYPE_CHOICES = (
        ('Faculty', 'Faculty'),
        ('Student', 'Student'),
    )
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=(('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')),
        default='Pending'
    )
    date = models.DateField(auto_now_add=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
 # Optional start date for leave
    def __str__(self):
        return f"{self.user.username} ({self.user_type}) - {self.status} - {self.start_date} to {self.end_date}"
    
    
# assignment (faculty) 
class Assignment(models.Model):
    SEMESTER_CHOICES = (
        ('Semester 1', 'Semester 1'),
        ('Semester 2', 'Semester 2'),
        ('Semester 3', 'Semester 3'),
        ('Semester 4', 'Semester 4'),
        ('Semester 5', 'Semester 5'),
        ('Semester 6', 'Semester 6'),
        ('Semester 7', 'Semester 7'),
        ('Semester 8', 'Semester 8'),
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20,choices=SEMESTER_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', null=True, blank=True)


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
