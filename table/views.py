import logging
from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from table.models import *
from table.controller import *
from table.forms import UploadTableForm
from authentication.models import UserProfile, UserProfileForm

log = logging.getLogger(__name__)

@login_required
def index(request):
    try:
        userprofile_form = UserProfile.objects.get(user_id=request.user.id)
    except ObjectDoesNotExist:
        userprofile_form = UserProfile(user=request.user)
    if request.method == 'POST':
        userprofile = UserProfileForm(request.POST, instance=userprofile_form)
        if userprofile.is_valid():
            userprofile.save()
    return render(request, 'table/index.html', {
        'timetable': TimeTable(request.user),
        'uploadform': UploadTableForm(),
        'loggingin_user': request.user,
        'userprofileform': UserProfileForm(instance=userprofile_form)
    })


@login_required
def uploadtable(request):
    contents = {
        'timetable': TimeTable(user=request.user),
        'upload_error': 'NO',
        'uploadform': UploadTableForm(),
    }
    if request.method == 'POST':
        form = UploadTableForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                update_table(file=request.FILES['file'].file, user=request.user)
            except UnicodeDecodeError:
                contents['upload_error'] = 'UnicodeError'
            return render(request, 'table/index_upload.html', contents)
    return render(request, 'table/index_upload.html', contents)


@login_required
def show_detail(request, subject_id):
    # その科目の所有ユーザーでないなら404
    if Subject.objects.get(id=subject_id).user_id != request.user.id:
        raise Http404("Subject does not exist")
    attendances = modelformset_factory(Attendance, extra=0, fields=('absence',))
    if request.method == 'POST':
        formset = attendances(request.POST)
        if formset.is_valid():
            formset.save()
    else:
        formset = attendances(queryset=Attendance.objects \
                              .filter(subject=subject_id).order_by('times'))
    return render(request, 'table/detail.html', {
        'subject': Subject.objects.get(id=subject_id),
        'attendances': Attendance.objects.filter(subject=subject_id).order_by('times'),
        'attend_formset': formset,
    })
