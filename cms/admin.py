from django.contrib import admin
from cms.models import Subject, Attendance


# Register your models here.

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'period', 'day')
    list_display_links = ('id', 'name')


admin.site.register(Subject, SubjectAdmin)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'times', 'absence')
    list_display_links = ('id',)


admin.site.register(Attendance, AttendanceAdmin)
