from __future__ import absolute_import, unicode_literals, print_function
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
from .anonymous import anonymous_project_view

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

def start_anonymous_project():
    initialise_all_callbacks()
    body = js.globals.document.body

    error_404_page = c("div", [c("p", "No match 404 error"),
                               c("p", [c("a", {"href": "/#!"}, "Back to main page")])])

    #TODO: A router is not actually needed here. We could just mount to the body. But
    # Some functions may require it. Could back and eliminate it later
    r = Router({r'^$': anonymous_project_view(),
                },
                error_404_page, body)
    r.route()
