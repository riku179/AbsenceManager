from django.db import models
from django import forms
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    watch_tl = models.BooleanField('TL監視', default=False)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['watch_tl', 'user']
