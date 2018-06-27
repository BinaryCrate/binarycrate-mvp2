# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.conf.urls import url
from applicationpage.views import ApplicationPageView


app_name = 'applicationpage'


urlpatterns = [

    url(r'^$', ApplicationPageView.as_view(), name='applicationpage'),



]
