"""
URL configuration for college_managment_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from  CMS import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),

    # ========== HOD ==========
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    
    # Student Management
    path('hod/manage-student/', views.manage_student, name='manage_student'),
    path("hod/manage_student/add", views.add_student, name="add_student"),
    path('hod/manage-student/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    
    # Faculty Management
    path('hod/manage-faculty/', views.manage_faculty, name='manage_faculty'),
    path("hod/manage_faculty/add", views.add_faculty, name="add_faculty"),
    path('hod/manage-faculty/delete/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    
    # Attendance  (NOT REQUIRED)
    # path('hod/manage-attendance/', views.manage_attendance, name='manage_attendance'),
    # # path('hod/view-attendance/', views.view_attendance, name='view_attendance'),
    # path('hod/view-attendance/<int:subject_id>/', views.view_attendance, name='view_attendance'),
    # path('hod/toggle-attendance/<int:report_id>/', views.toggle_attendance, name='toggle_attendance'),
    
    # Results
    path('hod/review-result/', views.review_result, name='review_result'),

    # Timetable
    path('hod/make-timetable/', views.make_timetable, name='make_timetable'),
    path('hod/delete-timetable/<int:timetable_id>/', views.delete_timetable, name='delete_timetable'),
    # path('ajax/load-subjects/', views.load_subjects, name='ajax_load_subjects'),


    # Leave Applications
    path("manage/leave/", views.view_leave, name="view_leave"),
    path("manage/leave/student/<int:leave_id>/<str:action>/", views.approve_leave_student, name="approve_leave_student"),
    path("manage/leave/faculty/<int:leave_id>/<str:action>/", views.approve_leave_faculty, name="approve_leave_faculty"),
    
    

    # ========== FACULTY ==========
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),

    # Attendance
    path('faculty/mark-attendance/', views.mark_attendance, name='mark_attendance'),

    # Results
    path('faculty/student-grade/', views.student_grade, name='student_grade'),

    # Assignment
    path('faculty/student-assignment/', views.student_assignment, name='student_assignment'),
    path('faculty/student-submission/', views.student_submission, name='student_submission'),
    path('faculty/approve-submission/<int:submission_id>/', views.approve_submission, name='approve_submission'),

    # Timetable
    path('faculty/timetable/', views.faculty_timetable, name='faculty_timetable'),

    # Leave
    path('faculty/leave/', views.apply_leave_fact, name='apply_leave_fact'),

    # ========== STUDENT ==========
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),

    # Attendance
    path('student/attendance/', views.view_attendance, name='student_attendance'),
    
    path("student/timetable/", views.student_timetable, name="student_timetable"),

    # Result
    path('student/result/', views.result, name='student_result'),

    # Fees (optional if not implemented)
    path('student/fees/', views.fees, name='student_fees'),

    # Assignment Submission
    path('student/assignment/', views.assignment_submission, name='student_assignment'),

    # Feedback
    path('student/feedback/', views.feedback, name='student_feedback'),

    # Leave
    path('student/leave/', views.apply_leave, name='student_leave'),

    # ========== COMMON ==========
    path('logout/', views.logout_view, name='logout'),


]

