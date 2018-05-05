# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', views.ProjectList.as_view(), name='project-list'),
    url(r'^(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.ProjectDetail.as_view(), name='project-detail'),
    url(r'^directoryentry/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.DirectoryEntryDetail.as_view(), name='directoryentry-detail'),
    url(r'^image/$', views.ImageUploadView.as_view(), name='image-upload'),
    url(r'^image-list/(?P<project>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.ImageListView.as_view(), name='image-list'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

