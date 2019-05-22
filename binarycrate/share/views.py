# -*- coding: utf-8 -*-
# BinaryCrate -  BinaryCrate an in browser python IDE. Design to make learning coding easy.
# Copyright (C) 2018 BinaryCrate Pty Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals

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
