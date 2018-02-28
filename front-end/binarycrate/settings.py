from __future__ import absolute_import, print_function
import cavorite
from cavorite import c, t, Router, get_current_hash
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy
from .navigation import BCChrome
import cavorite.bootstrap.modals as modals
from cavorite.bootstrap.modals import ModalTrigger, Modal
from cavorite.ajaxget import ajaxget, ajaxpost, ajaxput, ajaxdelete
from cavorite import timeouts
import json


class SettingView(BCChrome):
    def settings_tab(self):
        return



    # def my_details(self):

def settings_view():
    dv = SettingView([
                      li({'class': 'nav-item li-create-new'}, [
                        form({'action': '#'}, [
                          ModalTrigger({'class': "btn btn-default navbar-btn crt-btn"}, "Create New", "#createNew"),
                        ]),
                      ]),
                    ],
                    div([p("Hello")]),
                    [])
    return dv
