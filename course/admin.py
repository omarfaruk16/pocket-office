from django.contrib import admin
from .models import (
    Course, Part,
    ClassSession, AttendanceRecord,
    ClassTest, TestMark,
    Exam, ExamMark
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ['name', 'code', 'credit', 'semester__name']
    list_display = ['name', 'code', 'credit', 'semester_name']
    prepopulated_fields = {"slug": ("name",)}

    def semester_name(self, obj):
        return obj.semester.name if obj.semester else 'No Semester Assigned'
    semester_name.admin_order_field = 'semester__name'
    semester_name.short_description = 'Semester'

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    search_fields = ['course__semester__name', 'course__name', 'name', 'teacher__user__first_name']
    list_display = ['semester_name', 'course_name', 'name', 'teacher_name']

    def course_name(self, obj):
        return obj.course.name
    course_name.admin_order_field = 'course__name'
    course_name.short_description = 'Course'

    def teacher_name(self, obj):
        return obj.teacher.user.first_name if obj.teacher else 'No Teacher Assigned'
    teacher_name.admin_order_field = 'teacher__user__first_name'
    teacher_name.short_description = 'Teacher'

    def semester_name(self, obj):
        return obj.course.semester.name if obj.course and obj.course.semester else 'No Semester Assigned'
    semester_name.admin_order_field = 'course__semester__name'
    semester_name.short_description = 'Semester'

@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    search_fields = ['part__course__code', 'topic']
    list_display = ['date', 'topic', 'part_name', 'total_present']

    def part_name(self, obj):
        return f"{obj.part.course.code} - Part {obj.part.name}"
    part_name.short_description = 'Part'

    def total_present(self, obj):
        return obj.attendancerecord_set.filter(is_present=True).count()
    total_present.short_description = 'Total Present'

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'student__student_id']
    list_display = ['session', 'student', 'is_present']

@admin.register(ClassTest)
class ClassTestAdmin(admin.ModelAdmin):
    search_fields = ['part__course__code', 'topic']
    list_display = ['number', 'topic', 'date', 'part_name']

    def part_name(self, obj):
        return f"{obj.part.course.code} - Part {obj.part.name}"
    part_name.short_description = 'Part'

@admin.register(TestMark)
class TestMarkAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'test__topic']
    list_display = ['test', 'student', 'mark']

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    search_fields = ['part__course__code', 'title', 'topic']
    list_display = ['title', 'topic', 'date', 'part_name']

    def part_name(self, obj):
        return f"{obj.part.course.code} - Part {obj.part.name}"
    part_name.short_description = 'Part'

@admin.register(ExamMark)
class ExamMarkAdmin(admin.ModelAdmin):
    search_fields = ['student__name', 'exam__title']
    list_display = ['exam', 'student', 'mark']