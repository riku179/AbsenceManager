from django.shortcuts import render_to_response
from django.template import RequestContext
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
    if request.method == 'POST':
        formset = AttendanceFormSet(request.POST)
        if formset.is_valid():
            formset.save()
    else:
        formset = AttendanceFormSet()
    return render_to_response('cms/detail.html', {
        'subject': Subject.objects.get(id=subject_id),
        'attendances': Attendance.objects.filter(subject=subject_id).order_by('times'),
        'attend_formset': formset
    }, context_instance=RequestContext(request))
