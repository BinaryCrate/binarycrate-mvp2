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
from cavorite import c, t, Router, callbacks, timeouts, get_current_hash
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy
from .controls import CodeMirrorHandlerVNode
import uuid
from cavorite.bootstrap.modals import ModalTrigger, Modal


def navitem(title, icon_class, href, onclick=None):
    return li({'class':"nav-item", 'data-toggle':"tooltip", 'data-placement':"right", 'title':title, 'onclick': onclick}, [
             a({'class':"nav-link", 'href': href, 'style': {'min-height': '56px'}, 'onclick': onclick}, children=[
             #a({'class':"nav-link", 'style': {'min-height': '56px'}, 'onclick': onclick}, children=[
               i({'class': ["fa", "fa-fw"] + [icon_class], 'onclick': onclick}),
               span({'class':"nav-link-text", 'onclick': onclick}, title),
             ]),
           ])


def navsubmenu(title, parent_id, sublist_id, subitems):
    return \
    li({'class': 'nav-item', 'data-toggle': 'tooltip', 'data-placement': 'right', 'title': title}, [
      a({'class': 'nav-link nav-link-collapse collapsed', 'data-toggle': 'collapse', 'href': '#' + sublist_id, 'data-parent':'#' + parent_id}, [
        i({'class': "fa fa-fw fa-wrench"}),
        span({'class': "nav-link-text"}, title),
      ]),
      ul({'class': "sidenav-second-level collapse", 'id':sublist_id}, subitems),
    ])

def navsubmenuitem(title, url):
    return li([a({'href': url}, title)])


class BCChrome(div):
    def collapse_menu(self, e):
        body = js.globals.document.body
        self.menu_collapsed = not self.menu_collapsed
        if self.menu_collapsed:
            body.classList.add("sidenav-toggled")
        else:
            body.classList.remove("sidenav-toggled")
        jquery = js.globals['$']
        jquery(".navbar-sidenav .nav-link-collapse").addClass("collapsed");
        jquery(".navbar-sidenav .sidenav-second-level, .navbar-sidenav .sidenav-third-level").removeClass("show");
        e.preventDefault()
        return False

    def __init__(self, top_navbar_items, central_content, modals):
        self.menu_collapsed = False
        self.top_navbar_items = top_navbar_items
        self.central_content = central_content
        self.modals = modals
        self.context_menu = None
        super(BCChrome, self).__init__()

    def get_top_navbar_items(self):
        return self.top_navbar_items

    def get_central_content(self):
        return self.central_content

    def get_modals(self):
        return self.modals

    def get_context_menu(self):
        return None

    def get_context_menu_list(self):
        context_menu = self.get_context_menu()
        if context_menu is None:
            ret = []
        else:
            ret = [context_menu]
        #print('get_context_menu_list ret=', ret)
        return ret

    def get_sidebar_nav_items(self):
        return [
                 navitem('Dashboard', 'fa-dashboard', '#!'),
                 #navitem('Editor', 'fa-code', '#!editor'),
                 #navitem('Classroom', 'fa-laptop', '#!classroom'),
                 #navsubmenu('Settings', 'exampleAccordion', 'collapseComponents', [
                 #  navsubmenuitem('Navbar', '#!navbar'),
                 #  navsubmenuitem('Cards', '#!cards'),
                 #])
               ]

    def get_logout_link(self):
        #TODO: It makes no logical sense for this function to be seperate from get_sidebar_nav_items
        # Find a way to roll them together
        return [
                 ul({'class': 'navbar-nav ml-auto'}, [
                   li({'class': 'nav-item'}, [
                     ModalTrigger({'class':"nav-link"}, [
                       i({'class': "fa fa-fw fa-sign-out"}),
                       t("Logout"),
                     ], "#logoutModal"),
                   ]),
                 ]),
               ]

    def logout_clicked(self, e, form_values):
        js.globals.window.location.href = '/accounts/logout'

    def get_children(self):
        return [
                nav({'class': "navbar navbar-expand-lg navbar-dark bg-dark fixed-top", 'id': 'mainNav'}, [
                  a({'class': "nav-link", 'id':"sidenavToggler", 'style':"padding: 0px 10px 0px 0px; color:white;"}, [
                    i({'class': "fa fa-fw fa-bars", "onclick": self.collapse_menu})
                  ]),
                  a({'class': "navbar-brand", 'href':"#!"}, "Binary Crate"),
                  html_button({'class':"navbar-toggler navbar-toggler-right",
                               'type':"button", 'data-toggle':"collapse",
                               'data-target':"#navbarResponsive", 'aria-controls':"navbarResponsive",
                               'aria-expanded':"false", 'aria-label':"Toggle navigation"}, [
                    span({'class': "navbar-toggler-icon"}),
                  ]),
                  div({'class':"collapse navbar-collapse", 'id':"navbarResponsive"}, [
                    ul({'class':"navbar-nav navbar-sidenav", 'id':"exampleAccordion"}, self.get_sidebar_nav_items()),
                    ul({'class': 'navbar-nav mr-auto'}, self.get_top_navbar_items()),
                  ] + self.get_logout_link()),
                ]),
                div({'class': "content-wrapper", 'style': {'padding-top': '1px'}}, [self.get_central_content()]),
                footer({'class': "sticky-footer"}, [
                  div({'class':"container"}, [
                    div({'class':"text-center"}, [
                      small("Copyright (C) Binary Crate 2018"),
                    ]),
                  ]),
                ]),
                Modal("logoutModal", "Logout", [
                  div("Select \"Logout\" below if you are ready to end your current session."),
                ], self.logout_clicked),
              ] + self.get_modals() + self.get_context_menu_list()
