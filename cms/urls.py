from django.conf.urls import url, include, patterns
from django.contrib import admin

urlpatterns = patterns('cms.views',
                       url(r'^$', 'index'),
                       )