# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

"""binarycrate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls
from wagtail.wagtailcore import urls as wagtail_urls

from search import views as search_views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),

    # Landing Page
    url(r'^', include('landingpage.urls')),

    # API
    url(r'^api/', include('api.urls')),

    # Shared projects
    url(r'^share/', include('share.urls')),

    # Wagtail
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^content/', include(wagtail_urls)),
    url(r'', include(wagtail_urls)),
    url(r'^search/$', search_views.search, name='search'),


    # These redirects are hack because django-allauth redirects us to weird places. Fix it to go somewhere reasonable by default
    url(r'^accounts/profile', RedirectView.as_view(url='/', permanent=False)),
    url(r'^accounts/signup/None', RedirectView.as_view(url='/', permanent=False)),

    # Image downloads
    url(r'^images/', include('project.image_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#Should be If settings.DEBUG:
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls')),
]
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
