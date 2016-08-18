from django.conf.urls import url, include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'detail/(?P<subject_id>\d+)', views.show_detail, name='detail'),
    url(r'^upload$', views.uploadtable, name='upload'),
]
