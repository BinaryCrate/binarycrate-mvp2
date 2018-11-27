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

from django.core.files import File
import mimetypes
from binarycrate.storage import project_media_storage
from .models import Project, Image
from django.http import HttpResponse, Http404


def download_image(request, project, image_id):
    #TODO: This is file for development but in product we need a way of sending
    # files that will not occupy UWSGI worker time like this does
    try:
        project = Project.objects.get(pk=project)
    except Project.DoesNotExist:
        raise Http404
    try:
        img = Image.objects.filter(project=project).get(id=image_id)
    except Image.DoesNotExist:
        raise Http404
    wrapper = project_media_storage.open(img.get_file_name(), 'rb')
    content_type = mimetypes.guess_type(img.name)[0]  # Use mimetypes to get file type
    response     = HttpResponse(wrapper,content_type=content_type)
    response['Content-Length']      = wrapper.size
    response['Content-Disposition'] = "attachment; filename=%s" %  img.name
    return response
