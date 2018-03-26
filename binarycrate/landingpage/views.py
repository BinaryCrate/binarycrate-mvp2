# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

# Create your views here.

class LandingPageView(LoginRequiredMixin, TemplateView):

    template_name = "landingpage.html"

    def get_context_data(self, **kwargs):
        context = super(LandingPageView, self).get_context_data(**kwargs)
        context['build_number'] = settings.BUILD_NUMBER
        return context


