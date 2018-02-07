from __future__ import absolute_import, print_function
try:
    import js
except ImportError:
    js = None
from cavorite import c, t, Router, callbacks, timeouts, ajaxget
from .dashboard import dashboard_view
from .editor import editor_view

def start():
    callbacks.initialise_global_callbacks()
    timeouts.initialise_timeout_callbacks()
    ajaxget.initialise_ajaxget_callbacks()
    body = js.globals.document.body

    error_404_page = c("div", [c("p", "No match 404 error"),
                               c("p", [c("a", {"href": "/#!"}, "Back to main page")])])


    r = Router({r'^$': dashboard_view(),
                r'^editor/(?P<project_id>[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})$': editor_view(),
                r'^editor$': editor_view(),
                },
                error_404_page, body)
    r.route()

