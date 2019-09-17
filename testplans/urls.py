from django.conf.urls import url

from . import views

from django.contrib import admin

app_name = 'testplans'

urlpatterns = [
    url(r'^$', views.TestplanListView.as_view(), name='testplan_list'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.TestplanDetailView.as_view(), name='testplan_detail'),
    url(r'^update_testplan/(?P<pk>[0-9]+)/$', views.update_testplan, name='update_testplan'),
    url(r'^delete_testplan/(?P<pk>[0-9]+)/$', views.TestplanDelete.as_view(), name='delete_testplan'),
    url(r'^archive_testplan/(?P<pk>[0-9]+)/(?P<to_archive>(?i)(true|false))/$', views.archive_testplan, name='archive_testplan'),
    url(r'^get_processes/$', views.get_processes, name='get_processes'),
    url(r'^get_wafers/$', views.get_wafers, name='get_wafers'),
    url(r'^create_new_testplan/$', views.create_testplan, name='create_testplan'),
    url(r'^form_submit/(?P<object>[\w-]+)/(?P<pk>[0-9]+)/$', views.form_submit, name='form_submit'),
    url(r'^download/(?P<path>.*)/$', views.download, name='download'),
]
