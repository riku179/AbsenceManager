from django.forms import ModelForm
from django.forms.formsets import formset_factory
from cms.models import Attendance


class AttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = ['absence',]

