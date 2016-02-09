from django.shortcuts import render_to_response
from django.http import HttpResponse
from cms.models import Subject
from cms.timetable import CreateTimeTable


def index(request):
    return render_to_response('cms/index.html', {
        'timetable': CreateTimeTable
    })
