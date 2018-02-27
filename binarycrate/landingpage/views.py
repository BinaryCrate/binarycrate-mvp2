# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class LandingPageView(LoginRequiredMixin, TemplateView):

    template_name = "landingpage.html"

