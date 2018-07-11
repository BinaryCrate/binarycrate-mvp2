# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .tasks import debug_task

class LandingPageView(LoginRequiredMixin, TemplateView):

    template_name = "landingpage.html"

    def get_context_data(self, **kwargs):
        #TODO: This task is included for example purposes for how to write them these debug tasks should be removed once real tasks are created
        debug_task.delay("Hello task")
        context = super(LandingPageView, self).get_context_data(**kwargs)
        context['build_number'] = settings.BUILD_NUMBER
        context['boot_file'] = 'bootbc.py'
        return context


