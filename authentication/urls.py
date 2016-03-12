from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.contrib.auth.views import login, logout

urlpatterns = patterns('',
                       url(r'^login$', 'django.contrib.auth.views.login'),
                       url(r'^logout$', 'django.contrib.auth.views.logout'),
                       )
