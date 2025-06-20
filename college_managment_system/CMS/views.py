from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from huggingface_hub import logout
from .models import *
from .models import LeaveRequest 
from datetime import date
from django.http import HttpResponseRedirect
from .forms import *
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            role = form.cleaned_data['role']
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.role == role:
                    login(request, user)
                    if role == 'student':
                        return redirect('student_dashboard')
                    elif role == 'faculty':
                        return redirect('faculty_dashboard')
                    elif role == 'hod':
                        return redirect('hod_dashboard')
                else:
                    messages.error(request, 'Incorrect role selected.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})



# ---------------- HOD VIEWS ----------------

@login_required
def hod_dashboard(request):
    hod_depaetment = request.user.hod.department
    student_count = Student.objects.filter(department=hod_depaetment).count()
    faculty_count = Faculty.objects.filter(department=hod_depaetment).count()
    subject_count = Subject.objects.filter(department=hod_depaetment).count()
    return render(request, "hod_dashboard.html", {
        "student_count": student_count,
        "faculty_count": faculty_count,
        "subject_count": subject_count
    })

from django.db.models import Q

@login_required
def manage_student(request):
    hod_department = request.user.hod.department

    roll_query = request.GET.get('roll_number', '').strip()
    year_query = request.GET.get('year', '').strip()

    students = Student.objects.filter(department=hod_department)

    if roll_query:
        students = students.filter(roll_number__icontains=roll_query)
    if year_query:
        students = students.filter(year=year_query)

    return render(request, "hod_manage_student.html", {
        "students": students,
        "roll_query": roll_query,
        "year_query": year_query
    })

@login_required
def add_student(request):
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST)
        student_form = StudentForm(request.POST)

        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 'student'
            user.role = 'student'
            user.save()

            student = student_form.save(commit=False)
            student.user = user
            student.department = request.user.hod.department
            student.save()

            messages.success(request, "Student added successfully.")
            return redirect('add_student')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = CustomUserForm()
        student_form = StudentForm()

    return render(request, 'hod_add_student.html', {
        'user_form': user_form,
        'student_form': student_form
    })

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.user.delete()
    student.delete()
    return redirect("manage_student")

@login_required
def manage_faculty(request):
    hod_department = request.user.hod.department

    username = request.GET.get('username', '').strip()

    faculties = Faculty.objects.filter(department=hod_department)

    if username:
        faculties = faculties.filter(username__icontains=username)

    return render(request, "hod_manage_faculty.html", {
        "faculties": faculties,
        "username": username,
    })


@login_required
def add_faculty(request):
    if request.method == 'POST':
        user_form = CustomUserForm(request.POST)
        faculty_form = FacultyForm(request.POST)

        if user_form.is_valid() and faculty_form.is_valid():
            user = user_form.save(commit=False)
            user.user_type = 'faculty'
            user.role = 'faculty'
            user.save()

            faculty = faculty_form.save(commit=False)
            faculty.user = user
            faculty.department = request.user.hod.department
            faculty.save()

            messages.success(request, "Faculty added successfully.")
            return redirect('add_faculty')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = CustomUserForm()
        faculty_form = FacultyForm()

    return render(request, 'hod_add_faculty.html', {
        'user_form': user_form,
        'faculty_form': faculty_form
    })

@login_required
def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    faculty.user.delete()
    faculty.delete()
    return redirect("manage_faculty")


# @login_required
# def manage_attendance(request):
#     filter_form = AttendanceFilterForm(request.POST or None)
#     students = []
#     subject = None

#     if request.method == 'POST' and filter_form.is_valid():
#         semester = filter_form.cleaned_data['semester']
#         subject = filter_form.cleaned_data['subject']

#         # Filter students who are in that semester and have that subject
#         students = Student.objects.filter(
#             semester=semester , subjects=subject
#         )

#         if not students:
#             messages.info(request, "No students found for selected semester and subject.")
        
#     return render(request, "hod_manage_attendance.html", {
#         'filter_form': filter_form,
#         'students': students,
#         'subject': subject,
#     })  

from django.utils import timezone

@login_required
def manage_attendance(request):
    students = []
    subject = None
    semester = None

    if request.method == 'POST':
        semester = request.POST.get('semester')
        filter_form = AttendanceFilterForm(request.POST, semester=semester)

        if 'load_students' in request.POST and filter_form.is_valid():
            subject = filter_form.cleaned_data['subject']
            students = Student.objects.filter(semester=semester)

        elif 'submit_attendance' in request.POST:
            subject_id = request.POST.get("subject")
            if subject_id:
                subject = Subject.objects.get(id=subject_id)
            else:
                # Handle error: maybe redirect back with message
                messages.error(request, "Subject not selected.")
                return redirect('manage_attendance')

            semester = request.POST.get('semester')
            subject = Subject.objects.get(id=subject_id)
            students = Student.objects.filter(semester=semester)

            attendance_obj, _ = Attendance.objects.get_or_create(
                subject=subject,
                faculty=subject.faculty,
                date=timezone.now().date()
            )

            for student in students:
                status_key = f'student_{student.id}'
                status_val = request.POST.get(status_key)
                status = True if status_val == 'present' else False

                AttendanceReport.objects.update_or_create(
                    student=student,
                    attendance=attendance_obj,
                    defaults={'status': status}
                )

            messages.success(request, "Attendance submitted successfully.")
            return redirect('manage_attendance')
    else:
        filter_form = AttendanceFilterForm()

    return render(request, 'hod_manage_attendance.html', {
        'filter_form': filter_form,
        'students': students,
        'subject': subject
    })


@login_required
def view_attendance(request, subject_id):
    attendance = Attendance.objects.filter(subject_id=subject_id)
    return render(request, "view_attendance.html", {"attendance": attendance})

@login_required
def toggle_attendance(request, report_id):
    report = get_object_or_404(AttendanceReport, id=report_id)
    report.status = not report.status
    report.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def review_result(request):
    hod = get_object_or_404(HOD,user=request.user)

    # Filter results based on department's students
    results = StudentResult.objects.filter(
        student__department=hod.department,
        reviewed_by_HOD=False
    )

    if request.method == 'POST':
        result_id = request.POST.get('result_id')
        action = request.POST.get('action')

        result = get_object_or_404(StudentResult, id=result_id)

        if action == 'approve':
            result.status = 'Reviewed'
            result.reviewed_by_HOD = True
            result.save()
        elif action == 'reject':
            result.status = 'Rejected'
            result.reviewed_by_HOD = True
            result.save()

        return redirect('review_result')

    return render(request, 'hod_review_result.html', {'results': results})

@login_required
def make_timetable(request):
    timetables = Timetable.objects.all().order_by('day', 'start_time')
    form = TimetableForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Timetable entry added successfully.")
            return redirect('make_timetable')
        else:
            messages.error(request, "Please correct the error below.")

    return render(request, 'hod_manage_timetable.html', {
        'form': form,
        'timetables': timetables
    })

# @login_required
# def make_timetable(request):
#     form = TimetableForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         form.save()
#         messages.success(request, "Timetable entry added.")
#         return redirect('make_timetable')

#     timetables = Timetable.objects.all()
#     return render(request, 'hod_manage_timetable.html', {
#         'form': form,
#         'timetables': timetables
#     })


# @login_required
# def load_subjects(request):
#     department_id = request.GET.get('department_id')
#     semester = request.GET.get('semester')
#     subjects = Subject.objects.filter(department_id=department_id, semester=semester)
#     data = [{'id': s.id, 'name': s.name} for s in subjects]
#     return JsonResponse({'subjects': data})

@login_required
def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id)
    timetable.delete()
    messages.success(request, "Timetable entry deleted.")
    return redirect('make_timetable')



@login_required
def view_leave(request):
    student_leaves = LeaveRequest.objects.all().filter(user_type = "Student").order_by('-date')
    faculty_leaves = LeaveRequest.objects.all().filter(user_type = "Faculty").order_by('-date')
    return render(request, "hod_review_leave.html", {
        "student_leaves": student_leaves,
        "faculty_leaves": faculty_leaves
    })

@login_required
def approve_leave_student(request, leave_id, action):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'Approved' if action == 'approve' else 'Rejected'
    leave.save()
    return redirect("view_leave")

@login_required
def approve_leave_faculty(request, leave_id, action):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'Approved' if action == 'approve' else 'Rejected'
    leave.save()
    return redirect("view_leave")


# ---------------- FACULTY VIEWS ----------------

@login_required
def faculty_dashboard(request):
    faculty = request.user.faculty
    subject_count = Subject.objects.filter(faculty=faculty).count()
    return render(request, "faculty_dashboard.html", {"subject_count": subject_count})


# @login_required
# def mark_attendance(request):
#     faculty = request.user.faculty  # assuming CustomUser is linked to Faculty
#     students = []
#     subject_form = None
#     subject_selected = None
#     semester_selected = None

#     if request.method == 'POST':
#         semester_form = SemesterForm(request.POST)
#         if 'load_subjects' in request.POST and semester_form.is_valid():
#             semester_selected = semester_form.cleaned_data['semester']
#             subject_form = SubjectForm(faculty, semester_selected)
        
#         elif 'load_students' in request.POST:
#             semester_form = SemesterForm(request.POST)
#             if semester_form.is_valid():
#                 semester_selected = semester_form.cleaned_data['semester']
#             subject_form = SubjectForm(faculty, semester_selected, request.POST)
#             if semester_form.is_valid() and subject_form.is_valid():
#                 subject_selected = subject_form.cleaned_data['subject']
#                 students = Student.objects.filter(semester=semester_selected, department=subject_selected.department)


#         elif 'submit_attendance' in request.POST:
#             subject_id = request.POST.get('subject')
#             subject =   get_object_or_404(Subject, id=subject_id)
#             attendance = Attendance.objects.create(
#                 subject=subject,
#                 date=timezone.now().date(),
#                 faculty=faculty
#             )
#             for key, value in request.POST.items():
#                 if key.startswith('status_'):
#                     student_id = key.split('_')[1]
#                     student = Student.objects.get(id=student_id)
#                     AttendanceReport.objects.create(
#                         student=student,
#                         attendance=attendance,
#                         status=(value == 'Present')
#                     )
#             return redirect('mark_attendance')
#     else:
#         semester_form = SemesterForm()

#     return render(request, 'faculty_mark_attendance.html', {
#         'semester_form': semester_form,
#         'subject_form': subject_form,
#         'students': students,
#         'semester_selected': semester_selected,
#         'subject_selected': subject_selected,
#     }) 


@login_required
def mark_attendance(request):
    faculty = request.user.faculty
    students = []
    subject_form = None
    subject_selected = None
    semester_selected = None

    if request.method == 'POST':
        semester_form = SemesterForm(request.POST)
        
        # Load subjects after semester is selected
        if 'load_subjects' in request.POST and semester_form.is_valid():
            semester_selected = semester_form.cleaned_data['semester']
            subject_form = SubjectForm(faculty, semester_selected)

        # Load students after subject is selected
        elif 'load_students' in request.POST:
            if semester_form.is_valid():
                semester_selected = semester_form.cleaned_data['semester']
                subject_form = SubjectForm(faculty, semester_selected, request.POST)
                if subject_form.is_valid():
                    subject_selected = subject_form.cleaned_data['subject']
                    students = Student.objects.filter(
                        semester=semester_selected,
                        department=subject_selected.department
                    )

        # Submit attendance
        elif 'submit_attendance' in request.POST:
            subject_id = request.POST.get('subject')
            subject = get_object_or_404(Subject, id=subject_id)
            semester_form = SemesterForm()  # reset
            subject_form = SubjectForm(faculty, subject.semester)

            attendance = Attendance.objects.create(
                subject=subject,
                date=timezone.now().date(),
                faculty=faculty
            )
            for key, value in request.POST.items():
                if key.startswith('status_'):
                    student_id = key.split('_')[1]
                    student = Student.objects.get(id=student_id)
                    AttendanceReport.objects.create(
                        student=student,
                        attendance=attendance,
                        status=(value == 'Present')
                    )
            messages.success(request, "Attendance marked successfully.")
            return redirect('mark_attendance')  # refresh page to show success

    else:
        semester_form = SemesterForm()

    return render(request, 'faculty_mark_attendance.html', {
        'semester_form': semester_form,
        'subject_form': subject_form,
        'students': students,
        'semester_selected': semester_selected,
        'subject_selected': subject_selected,
    })  




@login_required
def student_grade(request):
    semester_form = SemesterForm(request.POST or None)
    grade_form = None
    semester = None

    if request.method == 'POST':
        if 'load' in request.POST and semester_form.is_valid():
            semester = semester_form.cleaned_data['semester']
            grade_form = GradeEntryForm(faculty=request.user.faculty, semester=semester)
        elif 'submit_grade' in request.POST:
            semester = int(request.POST.get('semester'))
            grade_form = GradeEntryForm(faculty=request.user.faculty, semester=semester, data=request.POST)
            if grade_form.is_valid():
                student = grade_form.cleaned_data['student']
                subject = grade_form.cleaned_data['subject']
                grade = grade_form.cleaned_data['grade']
                faculty = request.user.faculty

                # Save result
                StudentResult.objects.create(
                    student=student,
                    subject=subject,
                    grade=grade,
                    faculty=faculty,
                    semester=semester
                )
                messages.success(request, "Grade submitted successfully.")
                return redirect('student_grade')

    context = {
        'semester_form': semester_form,
        'grade_form': grade_form,
        'semester': semester
    }
    return render(request, 'faculty_student_grade.html', context)


@login_required
def faculty_assignment(request):
    faculty = request.user.faculty
    semester_selected = None
    subjects = None
    assignment_form = None

    if request.method == 'POST':
        semester_form = SemesterForm(request.POST)
        assignment_form = AssignmentForm(request.POST, request.FILES)

        if 'load_subjects' in request.POST and semester_form.is_valid():
            semester_selected = semester_form.cleaned_data['semester']
            subjects = Subject.objects.filter(semester=semester_selected, faculty=faculty)
            assignment_form = AssignmentForm()
            assignment_form.fields['subject'].queryset = subjects

        elif 'submit_assignment' in request.POST:
            if semester_form.is_valid() and assignment_form.is_valid():
                assignment = assignment_form.save(commit=False)
                assignment.faculty = faculty
                assignment.semester = semester_form.cleaned_data['semester']
                assignment.save()
                return redirect('faculty_assignment')

    else:
        semester_form = SemesterForm()

    context = {
        'semester_form': semester_form,
        'assignment_form': assignment_form,
        'semester_selected': semester_selected,
    }
    return render(request, 'faculty_student_assignment.html', context)

@login_required
def student_submission(request):
    faculty = request.user.faculty
    submissions = Submission.objects.filter(assignment__faculty=faculty)
    return render(request, "faculty_student_submission.html", {"submissions": submissions})

@login_required
def approve_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    submission.approved = True
    submission.save()
    return redirect("student_submission")

@login_required
def faculty_timetable(request):
    faculty = request.user.faculty  # assuming `request.user` is linked to Faculty model via OneToOne
    timetable = Timetable.objects.filter(faculty=faculty).order_by('day', 'start_time')

    # Organize timetable day-wise
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_wise_timetable = {day: [] for day in days}
    for entry in timetable:
        day_wise_timetable[entry.day].append(entry)

    context = {
        'day_wise_timetable': day_wise_timetable
    }
    return render(request, 'faculty_timetable.html', context)

@login_required
def apply_leave_fact(request):
    user = request.user
    if not hasattr(user, 'faculty'):
        return redirect('home')  # or show unauthorized

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = user
            leave.user_type = 'Faculty'
            leave.save()
            return redirect('apply_leave_fact')  # redirect to same page or leave history
    else:
        form = LeaveRequestForm()

    leave_requests = LeaveRequest.objects.filter(user=user).order_by('-date')
    return render(request, 'faculty_apply_leave.html', {'form': form, 'leave_requests': leave_requests})



# ---------------- STUDENT VIEWS ----------------

@login_required # done
def student_dashboard(request):
    student = request.user.student
    subjects = Subject.objects.filter(department=student.department)
    return render(request, "student_dashboard.html", {"subjects": subjects})

@login_required
def view_attendance(request):
    student = request.user.student
    reports = AttendanceReport.objects.filter(student=student)
    return render(request, "student_attendance.html", {"reports": reports})

@login_required
def student_timetable(request):
    return render(request, 'student_timetable.html')

@login_required
def result(request):
    student = request.user.student
    results = StudentResult.objects.filter(student=student)
    return render(request, "student_result.html", {"results": results})

@login_required
def fees(request):
    student = request.user.student
    fees = Fee.objects.filter(student=student)
    return render(request, "student_fees.html", {"fees": fees})

@login_required #done 
def assignment_submission(request):
    student = request.user.student
    assignments = Assignment.objects.filter(subject__department=student.department)
    submissions = Submission.objects.filter(student=student)
    if request.method == "POST":
        assignment_id = request.POST['assignment']
        file = request.FILES['file']
        assignment = Assignment.objects.get(id=assignment_id)
        Submission.objects.create(assignment=assignment, student=student, file=file)
        return redirect("student_assignment")
    return render(request, "student_assignment.html", {
        "assignments": assignments,
        "submissions": submissions
    })

@login_required 
def feedback(request):
    student = request.user.student
    if request.method == "POST":
        feedback_text = request.POST['feedback']
        Feedback.objects.create(student=student, feedback_text=feedback_text)
        messages.success(request, "Your feedback has been submitted successfully!")
        return redirect("student_feedback")
    return render(request, "student_feedback.html")

@login_required #done
def student_leave(request):
    user = request.user
    if not hasattr(user, 'student'):
        return redirect('home')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = user
            leave.user_type = 'Student'
            leave.save()
            return redirect('student_leave')
    else:
        form = LeaveRequestForm()
    leave_requests = LeaveRequest.objects.filter(user=user).order_by('-date')
    context = {
        'form': form, 
        'leave_requests': leave_requests
    }
    return render(request, 'student_apply_leave.html', context)

@login_required #done
def apply_leave_student(request):
    user = request.user
    if not hasattr(user, 'student'):
        return redirect('home')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = user
            leave.user_type = 'Student'
            leave.save()
            return redirect('apply_leave_student')
    else:
        form = LeaveRequestForm()

    leave_requests = LeaveRequest.objects.filter(user=user).order_by('-date')
    return render(request, 'student_apply_leave.html', {'form': form, 'leave_requests': leave_requests}) 


@login_required
def student_timetable(request):

    student = Student.objects.get(user=request.user)
    formatted_semester = f"Semester {student.semester}"
    # Fetch timetable for the student's department and semester
    timetable_entries = Timetable.objects.filter(
        department=student.department,
        semester=formatted_semester
    ).order_by('day', 'start_time')

    # Organize timetable day-wise
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_wise_timetable = {day: [] for day in days}
    for entry in timetable_entries:
        day_wise_timetable[entry.day].append(entry)

    context = {
        'timetable_by_day': day_wise_timetable,
    }
    return render(request, 'student_timetable.html', context)

@login_required # done
def student_view_attendance(request):
    student = request.user.student
    subjects = Subject.objects.filter(department=student.department, semester=student.semester)
    attendance_data = []

    for subject in subjects:
        attendance_reports = AttendanceReport.objects.filter(student=student, attendance__subject=subject)
        total_classes = attendance_reports.count()
        present_count = attendance_reports.filter(status='True').count()

        attendance_data.append({
            'subject': subject.name,
            'total_classes': total_classes,
            'present': present_count,
            'absent': total_classes - present_count,
            'percentage': (present_count / total_classes) * 100 if total_classes else 0
        })

    return render(request, 'student_view_attendance.html', {
        'attendance_data': attendance_data
    })


@login_required #done
def logout_view(request):
    logout(request)
    return redirect('home')


def assignments(request):
    student = request.user.student
    assignments = Assignment.objects.filter(subject__department=student.department, semester=student.semester)
    return render(request, "student_assignments.html", {"assignments": assignments})