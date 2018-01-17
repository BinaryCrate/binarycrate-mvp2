# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.snippet_list),
    url(r'^(?P<pk>[0-9]+)/$', views.snippet_detail),
]

