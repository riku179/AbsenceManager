from django.shortcuts import render_to_response
from django.http import HttpResponse
from cms.models import *
from cms.timetable import CreateTimeTable


def index(request):
    return render_to_response('cms/index.html', {
        'timetable': CreateTimeTable
    })


def show_detail(request, subject_id):
    return render_to_response('cms/detail.html', {
        'subject': Subject.objects.get(id=subject_id),
        'attendances': Attendance.objects.filter(subject=subject_id).order_by()
    })
