from __future__ import absolute_import, print_function
from cavorite import c, t, Router

class NavItem(c):
    def __init__(self, title, icon_class, href):
        super(NavItem, self).__init__("li", {'class':"nav-item", 'data-toggle':"tooltip", 'data-placement':"right", 'title':title}, [
            c("a", {'class': "nav-link", 'href': href}, [
                  c("i", {'class': "fa fa-fw " + icon_class}),
                    c("span", {'class': "nav-link-text"}, title),
                  ]),
            ])

class ProjectDropdownItem(c):
    def __init__(self, title, data_target):    
        super(ProjectDropdownItem, self).__init__("li", {'data-toggle':"modal", 'data-target':data_target}, [c("a", {'href': '#'}, title)])


projects = ['Pong Game', 'Resume Website', 'Twitter Clone', 'Website', 'Python Functions', 'Space Invaders']

class Project(c):
    def __init__(self, title):
        super(Project, self).__init__("div", {'class': "col-md-3 col-sm-4"}, [
          c("div", {'class': "wrimagecard wrimagecard-topimage" }, [
            c("div", {'class': "wrimagecard-topimage_header", 'style': "background-color: rgba(51, 105, 232, 0.1)"}, [
              c("center", [c("i", {'class': "fa fa-code fa-5x", 'style': "color:#3369e8"})]),
            ]),
            c("div", {'class': "wrimagecard-topimage_title"}, [
              c("div", {'class': 'dropdown'}, [
                c("li", {'class': "fa fa-pencil fa-lg edit", 'id': "menu1", 'data-toggle': "dropdown"}, [
                  c("ul", {'class': "dropdown-menu", 'role': "menu", 'aria-labelledby':"menu1"}, [
                    ProjectDropdownItem('Rename', "#renameProj"),
                    ProjectDropdownItem('Share', "#shareProj"),
                    ProjectDropdownItem('Delete', "#deleteProj"),
                  ]),
                ]),
              ]),
              c("p", title),
            ]),
          ]),
        ])

class Projects(c):
    def __init__(self):
        super(Projects, self).__init__("div", {'class': 'row'})

    def get_children(self):
        global projects
        return [Project(projname) for projname in projects]
             

dashboard_view = \
              c("div", [ 
                c("nav", {'class': "navbar navbar-expand-lg navbar-dark bg-dark fixed-top", 'id': 'mainNav'}, [
                  c("a", {'class': "nav-link", 'id':"sidenavToggler", 'style':"padding: 0px 10px 0px 0px; color:white;"}, [
                    c("i", {'class': "fa fa-fw fa-bars"})
                  ]),
                  c('a', {'class': "navbar-brand", 'href':"#!"}, "Binary Crate"),
                  c('button', {'class':"navbar-toggler navbar-toggler-right",
                               'type':"button", 'data-toggle':"collapse",
                               'data-target':"#navbarResponsive", 'aria-controls':"navbarResponsive",
                               'aria-expanded':"false", 'aria-label':"Toggle navigation"}, [
                    c('span', {'class': "navbar-toggler-icon"}),
                  ]),
                  c("div", {'class':"collapse navbar-collapse", 'id':"navbarResponsive"}, [
                    c("ul", {'class':"navbar-nav navbar-sidenav", 'id':"exampleAccordion"}, [
                      NavItem('Dashboard', 'fa-dashboard', '#!'),
                      NavItem('Editor', 'fa-area-chart', '#!editor'),
                      NavItem('Classrom', 'fa-table', '#!classroom'),
                    ]),
                    c("ul", {'class': 'navbar-nav mr-auto'}, [
                      c("li", {'class': 'nav-item'}, [
                        c("form", {'action': '#'}, [
                          c("button", {'class': "btn btn-default navbar-btn crt-btn", 'data-toggle': "modal", 'data-target':"#createNew"}, "Create New"),
                        ]),
                      ]),
                    ]),
                    c("ul", {'class': 'navbar-nav ml-auto'}, [
                      c("li", {'class': 'nav-item'}, [
                        c("a", {'class':"nav-link", 'data-toggle': "modal", 'data-target':"#exampleModal"}, [
                          c("i", {'class': "fa fa-fw fa-sign-out"}),
                          t("Logout"),
                        ]),
                      ]),
                    ]),
                  ]),
                ]),
                c("div", {'class': "content-wrapper"}, [c("div", {'class': "container-fluid"}, [
                  Projects(),
                ])]),
                c("footer", {'class': "sticky-footer"}, [
                  c("div", {'class':"container"}, [
                    c("div", {'class':"text-center"}, [
                      c("small", "Copyright (C) Binary Crate 2018"),
                    ]),
                  ]),
                ]),
              ])


