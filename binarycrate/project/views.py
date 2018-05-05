# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from django.core.files import File
import mimetypes
from binarycrate.storage import project_media_storage
from .models import Project, Image
from django.http import HttpResponse


def download_image(request, project, image_name):
    try:
        project = Project.objects.get(pk=project)
    except Project.DoesNotExist:
        raise Http404
    try:
        img = Image.objects.filter(project=project).get(name=image_name)
    except Image.DoesNotExist:
        raise Http404
    wrapper = project_media_storage.open(img.get_file_name(), 'rb')
    content_type = mimetypes.guess_type(image_name)[0]  # Use mimetypes to get file type
    response     = HttpResponse(wrapper,content_type=content_type)  
    response['Content-Length']      = wrapper.size
    response['Content-Disposition'] = "attachment; filename=%s" %  img.name
    return response

