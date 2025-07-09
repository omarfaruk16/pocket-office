from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Avg
from django.views import View
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
import django.db.models as models
import csv

from .models import (
    Part, Course,
    ClassSession, AttendanceRecord,
    ClassTest, TestMark,
    Exam, ExamMark
)
from student.models import Student
from teacher.models import Teacher

# ---------- TEACHER PART LIST DASHBOARD ----------
@method_decorator(login_required, name='dispatch')
class TeacherPartListView(View):
    def get(self, request):
        teacher = get_object_or_404(Teacher, user=request.user)
        parts = Part.objects.filter(teacher=teacher).select_related('course', 'course__semester')

        return render(request, 'course/teacher_part_list.html', {
            'teacher': teacher,
            'parts': parts
        })

# ---------- COMBINED SESSION LIST WITH PAGINATION, FILTER, SEARCH, EXPORT ----------
def all_sessions_combined(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    search = request.GET.get('search', '')
    session_type = request.GET.get('type', '')

    class_sessions = ClassSession.objects.filter(part=part)
    class_tests = ClassTest.objects.filter(part=part)
    exams = Exam.objects.filter(part=part)

    if search:
        class_sessions = class_sessions.filter(topic__icontains=search)
        class_tests = class_tests.filter(topic__icontains=search)
        exams = exams.filter(topic__icontains=search)

    if session_type == 'class':
        class_tests = exams = []
    elif session_type == 'ct':
        class_sessions = exams = []
    elif session_type == 'exam':
        class_sessions = class_tests = []

    class_sessions = class_sessions.values('id', 'date', 'time', 'topic').annotate(type=models.Value('class', output_field=models.CharField()))
    class_tests = class_tests.values('id', 'date', 'time', 'topic', 'number').annotate(type=models.Value('ct', output_field=models.CharField()))
    exams = exams.values('id', 'date', 'time', 'topic', 'title').annotate(type=models.Value('exam', output_field=models.CharField()))

    all_sessions = list(class_sessions) + list(class_tests) + list(exams)
    all_sessions.sort(key=lambda x: x['date'], reverse=True)

    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sessions.csv"'
        writer = csv.writer(response)
        writer.writerow(['Type', 'Date', 'Time', 'Topic'])
        for s in all_sessions:
            writer.writerow([s['type'], s['date'], s.get('time', ''), s['topic']])
        return response

    paginator = Paginator(all_sessions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'course/all_sessions.html', {
        'part': part,
        'page_obj': page_obj,
        'sessions': page_obj,
        'search': search,
        'session_type': session_type
    })

# ---------- CREATE CLASS SESSION ----------
def class_session_create(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    students = Student.objects.filter(semester=part.course.semester)

    if request.method == 'POST':
        topic = request.POST['topic']
        time = request.POST.get('time', '')
        session = ClassSession.objects.create(part=part, topic=topic, time=time)

        for student in students:
            present = request.POST.get(f'student_{student.id}', 'on') == 'on'
            AttendanceRecord.objects.create(session=session, student=student, is_present=present)

        return redirect('all_sessions_combined', part_id=part.id)

    return render(request, 'course/class_form.html', {'part': part, 'students': students})

# ---------- EDIT / DELETE CLASS SESSION ----------
def class_session_edit(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    students = Student.objects.filter(semester=session.part.course.semester)

    if request.method == 'POST':
        session.topic = request.POST['topic']
        session.time = request.POST.get('time', '')
        session.save()

        AttendanceRecord.objects.filter(session=session).delete()
        for student in students:
            present = request.POST.get(f'student_{student.id}', 'on') == 'on'
            AttendanceRecord.objects.create(session=session, student=student, is_present=present)

        return redirect('all_sessions_combined', part_id=session.part.id)

    attendance = {rec.student.id: rec.is_present for rec in AttendanceRecord.objects.filter(session=session)}
    return render(request, 'course/class_form.html', {'part': session.part, 'students': students, 'session': session, 'attendance': attendance})

def class_session_delete(request, session_id):
    session = get_object_or_404(ClassSession, id=session_id)
    part_id = session.part.id
    session.delete()
    return redirect('all_sessions_combined', part_id=part_id)

# ---------- CREATE / EDIT / DELETE CLASS TEST ----------
def class_test_create(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    students = Student.objects.filter(semester=part.course.semester)

    if request.method == 'POST':
        topic = request.POST['topic']
        time = request.POST.get('time', '')
        number = request.POST.get('number', 1)
        test = ClassTest.objects.create(part=part, topic=topic, time=time, number=number)

        for student in students:
            present = request.POST.get(f'student_{student.id}_present', 'on') == 'on'
            mark = request.POST.get(f'student_{student.id}_mark', '')
            TestMark.objects.create(test=test, student=student, is_present=present, mark=mark or None)

        return redirect('all_sessions_combined', part_id=part.id)

    return render(request, 'course/ct_form.html', {'part': part, 'students': students})

def class_test_edit(request, test_id):
    test = get_object_or_404(ClassTest, id=test_id)
    students = Student.objects.filter(semester=test.part.course.semester)

    if request.method == 'POST':
        test.topic = request.POST['topic']
        test.time = request.POST.get('time', '')
        test.number = request.POST.get('number', test.number)
        test.save()

        TestMark.objects.filter(test=test).delete()
        for student in students:
            present = request.POST.get(f'student_{student.id}_present', 'on') == 'on'
            mark = request.POST.get(f'student_{student.id}_mark', '')
            TestMark.objects.create(test=test, student=student, is_present=present, mark=mark or None)

        return redirect('all_sessions_combined', part_id=test.part.id)

    marks = {mark.student.id: (mark.is_present, mark.mark) for mark in TestMark.objects.filter(test=test)}
    return render(request, 'course/ct_form.html', {'part': test.part, 'students': students, 'test': test, 'marks': marks})

def class_test_delete(request, test_id):
    test = get_object_or_404(ClassTest, id=test_id)
    part_id = test.part.id
    test.delete()
    return redirect('all_sessions_combined', part_id=part_id)

# ---------- CREATE / EDIT / DELETE EXAM ----------
def exam_create(request, part_id):
    part = get_object_or_404(Part, id=part_id)
    students = Student.objects.filter(semester=part.course.semester)

    if request.method == 'POST':
        topic = request.POST['topic']
        title = request.POST['title']
        time = request.POST.get('time', '')
        exam = Exam.objects.create(part=part, topic=topic, title=title, time=time)

        for student in students:
            present = request.POST.get(f'student_{student.id}_present', 'on') == 'on'
            mark = request.POST.get(f'student_{student.id}_mark', '')
            ExamMark.objects.create(exam=exam, student=student, is_present=present, mark=mark or None)

        return redirect('all_sessions_combined', part_id=part.id)

    return render(request, 'course/exam_form.html', {'part': part, 'students': students})

def exam_edit(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    students = Student.objects.filter(semester=exam.part.course.semester)

    if request.method == 'POST':
        exam.topic = request.POST['topic']
        exam.title = request.POST['title']
        exam.time = request.POST.get('time', '')
        exam.save()

        ExamMark.objects.filter(exam=exam).delete()
        for student in students:
            present = request.POST.get(f'student_{student.id}_present', 'on') == 'on'
            mark = request.POST.get(f'student_{student.id}_mark', '')
            ExamMark.objects.create(exam=exam, student=student, is_present=present, mark=mark or None)

        return redirect('all_sessions_combined', part_id=exam.part.id)

    marks = {mark.student.id: (mark.is_present, mark.mark) for mark in ExamMark.objects.filter(exam=exam)}
    return render(request, 'course/exam_form.html', {'part': exam.part, 'students': students, 'exam': exam, 'marks': marks})

def exam_delete(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    part_id = exam.part.id
    exam.delete()
    return redirect('all_sessions_combined', part_id=part_id)

# ---------- STUDENT RESULT SUMMARY ----------
def student_result_summary(request, part_id, student_id):
    part = get_object_or_404(Part, id=part_id)
    student = get_object_or_404(Student, id=student_id)

    ct_results = TestMark.objects.filter(test__part=part, student=student).select_related('test')
    exam_results = ExamMark.objects.filter(exam__part=part, student=student).select_related('exam')

    return render(request, 'course/student_result_summary.html', {
        'part': part,
        'student': student,
        'ct_results': ct_results,
        'exam_results': exam_results,
    })

from django.shortcuts import render
from .models import Course, ClassSession, ClassTest, Exam, AttendanceRecord, TestMark, ExamMark
from student.models import Student
from django.shortcuts import render
from .models import Course, ClassSession, ClassTest, Exam, AttendanceRecord, TestMark, ExamMark
from student.models import Student

def course_detail(request, course_slug):
    course = Course.objects.get(slug=course_slug)
    
    # Fetch all students for this course
    students = Student.objects.all()
    
    # Fetch all class sessions, class tests, and exams for this course
    class_sessions = ClassSession.objects.filter(part__course=course)
    class_tests = ClassTest.objects.filter(part__course=course)
    exams = Exam.objects.filter(part__course=course)
    
    # Create a list to store attendance, test marks, and exam marks for each student
    attendance_data = []
    test_data = []
    exam_data = []

    for student in students:
        student_data = {}
        student_data['name'] = student.name
        student_data['roll_number'] = student.roll_number

        # Attendance for each class session
        attendance = {}
        for session in class_sessions:
            attendance[session.date] = AttendanceRecord.objects.filter(session=session, student=student).first()
        student_data['attendance'] = attendance

        # Marks for each class test
        test_marks = {}
        for test in class_tests:
            test_mark = TestMark.objects.filter(test=test, student=student).first()
            test_marks[test.topic] = test_mark.mark if test_mark else None
        student_data['test_marks'] = test_marks

        # Marks for each exam
        exam_marks = {}
        for exam in exams:
            exam_mark = ExamMark.objects.filter(exam=exam, student=student).first()
            exam_marks[exam.title] = exam_mark.mark if exam_mark else None
        student_data['exam_marks'] = exam_marks

        attendance_data.append(student_data)
    
    return render(request, 'course_detail.html', {
        'course': course,
        'students': students,
        'attendance_data': attendance_data,
        'class_sessions': class_sessions,
        'class_tests': class_tests,
        'exams': exams,
    })
