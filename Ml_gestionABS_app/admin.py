from django.contrib import admin
from .models import Student, ClassGroup, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name')
    search_fields = ('student_id', 'first_name', 'last_name')

@admin.register(ClassGroup)
class ClassGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    filter_horizontal = ('students',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_group', 'date', 'is_present', 'timestamp')
    list_filter = ('date', 'is_present', 'class_group')
    search_fields = ('student__student_id', 'student__first_name', 'student__last_name')