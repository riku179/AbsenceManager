from django import forms


class UploadTableForm(forms.Form):
    file = forms.FileField()
