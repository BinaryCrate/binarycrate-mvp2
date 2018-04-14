# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.views.generic.base import TemplateView
from project.models import Project
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings


class SharePageView(TemplateView):

    template_name = "sharedproject.html"

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=kwargs['project_id'])
        if project.public is False:
            raise Http404
        return super(SharePageView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SharePageView, self).get_context_data(**kwargs)
        context['build_number'] = settings.BUILD_NUMBER
        context['boot_file'] = 'boot_bc_shared_project.py'
        return context

