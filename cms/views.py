from django.shortcuts import render_to_response
from django.http import HttpResponse
from cms.models import Subject


def index(request):
    sorted_all_subjects = Subject.objects.all().order_by('day', 'period')
    return render_to_response('cms/index.html',
                              {'sorted_all_subjects': sorted_all_subjects})
