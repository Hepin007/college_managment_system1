from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Student)
admin.site.register(Faculty)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(Attendance)
admin.site.register(AttendanceReport)
admin.site.register(StudentResult)
admin.site.register(Timetable)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Feedback)
admin.site.register(LeaveRequest)
admin.site.register(Fee)
