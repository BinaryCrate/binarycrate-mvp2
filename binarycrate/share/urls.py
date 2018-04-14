# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from .views import SharePageView


app_name = 'share'


urlpatterns = [

    url(r'^(?P<project_id>[\w-]+)/$', SharePageView.as_view(), name='shared_project'),



]
