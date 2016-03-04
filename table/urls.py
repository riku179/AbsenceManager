from django.conf.urls import url, include, patterns
from django.contrib import admin

urlpatterns = patterns('table.views',
                       url(r'^$', 'index'),
                       url(r'detail/(?P<subject_id>\d+)', 'show_detail'),
                       url(r'^upload$', 'uploadtable'),
                       )
