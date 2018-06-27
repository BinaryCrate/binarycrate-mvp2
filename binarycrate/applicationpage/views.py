# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

class ApplicationPageView(LoginRequiredMixin, TemplateView):

    template_name = "applicationpage.html"

    def get_context_data(self, **kwargs):
        context = super(ApplicationPageView, self).get_context_data(**kwargs)
        context['build_number'] = settings.BUILD_NUMBER
        context['boot_file'] = 'bootbc.py'
        return context
