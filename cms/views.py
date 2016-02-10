from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.forms.models import modelformset_factory
from cms.models import *
from cms.timetable import CreateTimeTable


def index(request):
    return render_to_response('cms/index.html', {
        'timetable': CreateTimeTable
    })


def show_detail(request, subject_id):
    AttendanceFormSet = modelformset_factory(Attendance, extra=0, fields=('absence', ))
    formset = AttendanceFormSet()
    # Attendance.objects.filter(subject=subject_id).order_by('times'))
    return render_to_response('cms/detail.html', {
        'subject': Subject.objects.get(id=subject_id),
        'attendances': Attendance.objects.filter(subject=subject_id).order_by('times'),
        'attend_formset': formset
    })


def update_attendance_status(request, subject_id):
    pass
