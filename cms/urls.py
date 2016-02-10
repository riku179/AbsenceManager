from django.conf.urls import url, include, patterns
from django.contrib import admin

urlpatterns = patterns('cms.views',
                       url(r'^$', 'index'),
                       url(r'detail/(?P<subject_id>\d+)', 'show_detail'),
                       url(r'detail/(?P<subject_id>\d+)/update', 'update_attendance_status')
                       )
