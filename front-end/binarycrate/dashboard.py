from __future__ import absolute_import, print_function
from cavorite import c, t, Router
from cavorite.HTML import *
import js

def navitem(title, icon_class, href):
    return li({'class':"nav-item", 'data-toggle':"tooltip", 'data-placement':"right", 'title':title}, [
             a(href=href, cssClass="nav-link", children=[
               i(cssClass=["fa", "fa-fw"] + [icon_class]),
               span(title, cssClass="nav-link-text"),
             ]),
           ])

def projectdropdownitem(title, data_target):
    return li({'data-toggle':"modal", 'data-target':data_target}, [a(title, href='#')])


projects = ['Pong Game', 'Resume Website', 'Twitter Clone', 'Website', 'Python Functions', 'Space Invaders']

class Project(div):
    def __init__(self, title):
        super(Project, self).__init__(cssClass="col-md-3 col-sm-4", children=[
          div(cssClass="wrimagecard wrimagecard-topimage", children=[
            div(cssClass="wrimagecard-topimage_header", style="background-color: rgba(51, 105, 232, 0.1)", children=[
              center([i(cssClass="fa fa-code fa-5x", style="color:#3369e8")]),
            ]),
            div(cssClass="wrimagecard-topimage_title", children=[
              div(cssClass='dropdown', children=[
                li({'class': "fa fa-pencil fa-lg edit", 'id': "menu1", 'data-toggle': "dropdown"}, [
                  ul({'class': "dropdown-menu", 'role': "menu", 'aria-labelledby':"menu1"}, [
                    projectdropdownitem('Rename', "#renameProj"),
                    projectdropdownitem('Share', "#shareProj"),
                    projectdropdownitem('Delete', "#deleteProj"),
                  ]),
                ]),
              ]),
              p(title),
            ]),
          ]),
        ])

def projectsfn():
    return [Project(projname) for projname in projects]

body = js.globals.document.body

menu_collapsed = False

def collapse_menu(e):
    global menu_collapsed
    menu_collapsed = not menu_collapsed
    if menu_collapsed:
        body.classList.add("sidenav-toggled")
    else:
        body.classList.remove("sidenav-toggled")
    e.preventDefault()    
    return False

dashboard_view = \
              div([ 
                nav({'class': "navbar navbar-expand-lg navbar-dark bg-dark fixed-top", 'id': 'mainNav'}, [
                  a({'class': "nav-link", 'id':"sidenavToggler", 'style':"padding: 0px 10px 0px 0px; color:white;"}, [
                    i({'class': "fa fa-fw fa-bars", "onclick": collapse_menu})
                  ]),
                  a({'class': "navbar-brand", 'href':"#!"}, "Binary Crate"),
                  html_button({'class':"navbar-toggler navbar-toggler-right",
                               'type':"button", 'data-toggle':"collapse",
                               'data-target':"#navbarResponsive", 'aria-controls':"navbarResponsive",
                               'aria-expanded':"false", 'aria-label':"Toggle navigation"}, [
                    span({'class': "navbar-toggler-icon"}),
                  ]),
                  div({'class':"collapse navbar-collapse", 'id':"navbarResponsive"}, [
                    ul({'class':"navbar-nav navbar-sidenav", 'id':"exampleAccordion"}, [
                      navitem('Dashboard', 'fa-dashboard', '#!'),
                      navitem('Editor', 'fa-area-chart', '#!editor'),
                      navitem('Classrom', 'fa-table', '#!classroom'),
                    ]),
                    ul({'class': 'navbar-nav mr-auto'}, [
                      li({'class': 'nav-item'}, [
                        form({'action': '#'}, [
                          html_button({'class': "btn btn-default navbar-btn crt-btn", 'data-toggle': "modal", 'data-target':"#createNew"}, "Create New"),
                        ]),
                      ]),
                    ]),
                    ul({'class': 'navbar-nav ml-auto'}, [
                      li({'class': 'nav-item'}, [
                        a({'class':"nav-link", 'data-toggle': "modal", 'data-target':"#exampleModal"}, [
                          i({'class': "fa fa-fw fa-sign-out"}),
                          t("Logout"),
                        ]),
                      ]),
                    ]),
                  ]),
                ]),
                div({'class': "content-wrapper"}, [c("div", {'class': "container-fluid"}, [
                  div({'class': 'row'}, children=projectsfn),
                ])]),
                footer({'class': "sticky-footer"}, [
                  div({'class':"container"}, [
                    div({'class':"text-center"}, [
                      small("Copyright (C) Binary Crate 2018"),
                    ]),
                  ]),
                ]),
              ])


