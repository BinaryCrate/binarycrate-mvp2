# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.views.generic.base import TemplateView
from django.conf import settings


class ApplicationPageView(TemplateView):

    template_name = "applicationpage.html"

    def get_context_data(self, **kwargs):
        context = super(ApplicationPageView, self).get_context_data(**kwargs)
        context['build_number'] = settings.BUILD_NUMBER
        if self.request.user.is_anonymous:
            context['boot_file'] = 'bootbc_anonymous_user.py'
        else:
            context['boot_file'] = 'bootbc.py'
        return context
