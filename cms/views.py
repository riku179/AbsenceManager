from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory
from cms.models import *
from cms.controller import *
from cms.forms import UploadTableForm


def index(request):
    return render_to_response('cms/index.html', {
        'timetable': TimeTable(),
        'upload': False,
        'uploadform': UploadTableForm(),
    }, context_instance=RequestContext(request))


def uploadtable(request):
    if request.method == 'POST':
        form = UploadTableForm(request.POST, request.FILES)
        if form.is_valid():
            update_table(request.FILES['file'])
            return render_to_response('cms/index.html', {
                'timetable': TimeTable(),
                'upload': True,
                'uploadform': UploadTableForm(),
            })
    return render_to_response('cms/index.html', {
        'timetable': TimeTable(),
        'upload': 'False',
        'uploadform': UploadTableForm(),
    }, context_instance=RequestContext(request))


def show_detail(request, subject_id):
    attendances = modelformset_factory(Attendance, extra=0, fields=('absence',))
    if request.method == 'POST':
        formset = attendances(request.POST)
        if formset.is_valid():
            formset.save()
    else:
        formset = attendances(queryset=Attendance.objects \
                              .filter(subject=subject_id).order_by('times'))
    return render_to_response('cms/detail.html', {
        'subject': Subject.objects.get(id=subject_id),
        'attendances': Attendance.objects.filter(subject=subject_id).order_by('times'),
        'attend_formset': formset,

    }, context_instance=RequestContext(request))
