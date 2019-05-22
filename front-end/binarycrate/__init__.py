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
try:
    import js
except ImportError:
    js = None
from cavorite import c, t, Router, callbacks, timeouts, ajaxget
from .dashboard import dashboard_view
from .editor import editor_view
from .controls import codemirror
from .build_number import BUILD_NUMBER
from .sharedview import shared_view

def initialise_all_callbacks():
    callbacks.initialise_global_callbacks()
    timeouts.initialise_timeout_callbacks()
    ajaxget.initialise_ajaxget_callbacks()
    codemirror.initialise_codemirror_callbacks()

def start():
    initialise_all_callbacks()
    body = js.globals.document.body

    error_404_page = c("div", [c("p", "No match 404 error"),
                               c("p", [c("a", {"href": "/#!"}, "Back to main page")])])


    r = Router({r'^$': dashboard_view(),
                r'^editor/(?P<project_id>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})$': editor_view(),
                #r'^editor$': editor_view(),
                },
                error_404_page, body)
    r.route()

def start_shared_project():
    initialise_all_callbacks()
    body = js.globals.document.body

    error_404_page = c("div", [c("p", "No match 404 error"),
                               c("p", [c("a", {"href": "/#!"}, "Back to main page")])])

    #TODO: A router is not actually needed here. We could just mount to the body. But
    # Some functions may require it. Could back and eliminate it later
    r = Router({r'^$': shared_view(),
                },
                error_404_page, body)
    r.route()
