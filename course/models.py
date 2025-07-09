from django.db import models
from student.models import Semester, Student
from teacher.models import Teacher

# Part can be A or B
PartName = (
    ('A', 'A'),
    ('B', 'B'),
)

class Course(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    code = models.CharField(max_length=8)
    credit = models.IntegerField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    year = models.CharField(max_length=4, null= True, blank=True )
    

    def __str__(self):
        return f"{self.name} ({self.code})"

class Part(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(choices=PartName, max_length=2)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.course.code} - Part {self.name}"

# Shared abstract model for all session types
class BaseSession(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    topic = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    time = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True

# ---------- CLASS ----------
class ClassSession(BaseSession):
    def __str__(self):
        return f"Class on {self.date} - {self.topic}"

class AttendanceRecord(models.Model):
    session = models.ForeignKey(ClassSession, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.name} - {'Present' if self.is_present else 'Absent'}"

# ---------- CLASS TEST ----------
class ClassTest(BaseSession):
    number = models.PositiveIntegerField()

    def __str__(self):
        return f"CT {self.number} - {self.topic}"

class TestMark(models.Model):
    test = models.ForeignKey(ClassTest, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=True)
    mark = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - CT {self.test.number} - {self.mark if self.mark is not None else 'N/A'}"

# ---------- EXAM ----------
class Exam(BaseSession):
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"Exam - {self.title}"

class ExamMark(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    is_present = models.BooleanField(default=True)
    mark = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.name} - Exam {self.exam.title} - {self.mark if self.mark is not None else 'N/A'}"
