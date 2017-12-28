from __future__ import absolute_import, print_function
import js
from cavorite import c, t, Router
from .dashboard import dashboard_view

def start():
    body = js.globals.document.body

    error_404_page = c("div", [c("p", "No match 404 error"),
                               c("p", [c("a", {"href": "/#!"}, "Back to main page")])])


    r = Router({r'^$': dashboard_view,
                },
                error_404_page, body)
    r.route()

