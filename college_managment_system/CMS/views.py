from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from datetime import date
from django.http import HttpResponseRedirect

# ---------------- HOD VIEWS ----------------

@login_required
def hod_dashboard(request):
    student_count = Student.objects.count()
    faculty_count = Faculty.objects.count()
    subject_count = Subject.objects.count()
    return render(request, "hod_dashboard.html", {
        "student_count": student_count,
        "faculty_count": faculty_count,
        "subject_count": subject_count
    })

@login_required
def manage_student(request):
    students = Student.objects.all()
    return render(request, "manage_student.html", {"students": students})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.user.delete()
    student.delete()
    return redirect("manage_student")

@login_required
def manage_faculty(request):
    faculties = Faculty.objects.all()
    return render(request, "manage_faculty.html", {"faculties": faculties})

@login_required
def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    faculty.user.delete()
    faculty.delete()
    return redirect("manage_faculty")

@login_required
def manage_attendance(request):
    subjects = Subject.objects.all()
    return render(request, "manage_attendance.html", {"subjects": subjects})

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
    results = StudentResult.objects.select_related('student', 'subject')
    return render(request, "review_result.html", {"results": results})

@login_required
def make_timetable(request):
    timetables = Timetable.objects.all()
    subjects = Subject.objects.all()
    faculties = Faculty.objects.all()
    if request.method == "POST":
        subject_id = request.POST['subject']
        faculty_id = request.POST['faculty']
        day = request.POST['day']
        time = request.POST['time']
        subject = Subject.objects.get(id=subject_id)
        faculty = Faculty.objects.get(id=faculty_id)
        Timetable.objects.create(subject=subject, faculty=faculty, department=subject.department, day=day, time=time)
        return redirect("make_timetable")
    return render(request, "make_timetable.html", {
        "timetables": timetables,
        "subjects": subjects,
        "faculties": faculties
    })

@login_required
def delete_timetable(request, timetable_id):
    timetable = get_object_or_404(Timetable, id=timetable_id)
    timetable.delete()
    return redirect("make_timetable")

@login_required
def view_leave(request):
    leaves = LeaveRequest.objects.all().order_by('-date')
    return render(request, "view_leave.html", {"leaves": leaves})

@login_required
def approve_leave(request, leave_id, action):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    leave.status = 'Approved' if action == 'approve' else 'Rejected'
    leave.save()
    return redirect("view_leave")   


# ---------------- FACULTY VIEWS ----------------

@login_required
def faculty_dashboard(request):
    faculty = request.user.faculty
    subjects = Subject.objects.filter(faculty=faculty)
    return render(request, "faculty_dashboard.html", {"subjects": subjects})

@login_required
def mark_attendance(request, subject_id):
    students = Student.objects.filter(department=request.user.faculty.department)
    subject = Subject.objects.get(id=subject_id)
    if request.method == "POST":
        date_today = date.today()
        attendance = Attendance.objects.create(subject=subject, faculty=request.user.faculty, date=date_today)
        for student in students:
            status = request.POST.get(f'student_{student.id}') == 'on'
            AttendanceReport.objects.create(student=student, attendance=attendance, status=status)
        return redirect("faculty_dashboard")
    return render(request, "faculty_mark_attendance.html", {"students": students, "subject": subject})

@login_required
def student_grade(request, subject_id):
    students = Student.objects.filter(department=request.user.faculty.department)
    subject = get_object_or_404(Subject, id=subject_id)
    if request.method == "POST":
        for student in students:
            grade = request.POST.get(f'grade_{student.id}')
            result, _ = StudentResult.objects.get_or_create(student=student, subject=subject)
            result.grade = grade
            result.save()
        return redirect("faculty_dashboard")
    return render(request, "faculty_student_grade.html", {"students": students, "subject": subject})

@login_required
def student_assignment(request):
    faculty = request.user.faculty
    assignments = Assignment.objects.filter(faculty=faculty)
    subjects = Subject.objects.filter(faculty=faculty)
    if request.method == "POST":
        subject_id = request.POST['subject']
        title = request.POST['title']
        description = request.POST['description']
        due_date = request.POST['due_date']
        file = request.FILES['file']
        subject = Subject.objects.get(id=subject_id)
        Assignment.objects.create(subject=subject, faculty=faculty, title=title, description=description, due_date=due_date, file=file)
        return redirect("student_assignment")
    return render(request, "faculty_student_assignment.html", {"assignments": assignments, "subjects": subjects})

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
    timetable = Timetable.objects.filter(faculty=request.user.faculty)
    return render(request, "faculty_timetable.html", {"timetable": timetable})

@login_required
def apply_leave_fact(request):
    leaves = LeaveRequest.objects.filter(user=request.user)
    if request.method == "POST":
        reason = request.POST['reason']
        LeaveRequest.objects.create(user=request.user, user_type='Faculty', reason=reason)
        return redirect("apply_leave_fact")
    return render(request, "faculty_leave.html", {"leaves": leaves}) 



# ---------------- STUDENT VIEWS ----------------

@login_required
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
def result(request):
    student = request.user.student
    results = StudentResult.objects.filter(student=student)
    return render(request, "student_result.html", {"results": results})

@login_required
def fees(request):
    student = request.user.student
    fees = Fee.objects.filter(student=student)
    return render(request, "student_fees.html", {"fees": fees})

@login_required
def assignment_submission(request):
    student = request.user.student
    assignments = Assignment.objects.filter(subject__department=student.department)
    submissions = Submission.objects.filter(student=student)
    if request.method == "POST":
        assignment_id = request.POST['assignment']
        file = request.FILES['file']
        assignment = Assignment.objects.get(id=assignment_id)
        Submission.objects.create(assignment=assignment, student=student, file=file)
        return redirect("assignment_submission")
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
        return redirect("feedback")
    return render(request, "student_feedback.html")

@login_required
def apply_leave(request):
    leaves = LeaveRequest.objects.filter(user=request.user)
    if request.method == "POST":
        reason = request.POST['reason']
        LeaveRequest.objects.create(user=request.user, user_type='Student', reason=reason)
        return redirect("apply_leave")
    return render(request, "student_leave.html", {"leaves": leaves})