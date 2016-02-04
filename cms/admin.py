from django.contrib import admin
from cms.models import Subject, Attendance


# Register your models here.

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_name', 'period', 'day', 'absence')
    list_display_links = ('id', 'subject_name')


admin.site.register(Subject, SubjectAdmin)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'number_of_times', 'attendance')
    list_display_links = ('id',)


admin.site.register(Attendance, AttendanceAdmin)
