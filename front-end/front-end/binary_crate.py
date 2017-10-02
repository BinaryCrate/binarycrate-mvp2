from __future__ import absolute_import, print_function
import js
from cavorite import c, t, Router

body = js.globals.document.body

welcome_page = c("div", [c("p", "Binary Crate")])

error_404_page = c("div", [c("p", "No match 404 error"),
                           c("p", [c("a", {"href": "/#!"}, "Back to main page")])])

r = Router({r'^$': welcome_page},
            error_404_page, body)
r.route()



        
            
