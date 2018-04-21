# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.conf.urls import url
from landingpage.views import LandingPageView


app_name = 'landingpage'


urlpatterns = [

    url(r'^$', LandingPageView.as_view(), name='landingpage'),



]
