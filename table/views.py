from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory

from table.models import *
from table.controller import *
from table.forms import UploadTableForm


def index(request):
    return render_to_response('table/index.html', {
        'timetable': TimeTable(),
        'uploadform': UploadTableForm(),
    }, context_instance=RequestContext(request))


def uploadtable(request):
    contents = {
        'timetable': TimeTable(),
        'upload_error': 'NO',
        'uploadform': UploadTableForm(),
    }
    if request.method == 'POST':
        form = UploadTableForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                update_table(request.FILES['file'].file)
            except UnicodeDecodeError:
                contents['upload_error'] = 'UnicodeError'
            return render_to_response('table/index_upload.html', contents, context_instance=RequestContext(request))
    return render_to_response('table/index_upload.html', contents, context_instance=RequestContext(request))


def show_detail(request, subject_id):
    attendances = modelformset_factory(Attendance, extra=0, fields=('absence',))
    if request.method == 'POST':
        formset = attendances(request.POST)
        if formset.is_valid():
            formset.save()
    else:
        formset = attendances(queryset=Attendance.objects \
                              .filter(subject=subject_id).order_by('times'))
    return render_to_response('table/detail.html', {
        'subject': Subject.objects.get(id=subject_id),
        'attendances': Attendance.objects.filter(subject=subject_id).order_by('times'),
        'attend_formset': formset,
    }, context_instance=RequestContext(request))
