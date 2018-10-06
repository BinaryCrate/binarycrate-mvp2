from __future__ import absolute_import, print_function, unicode_literals
from cavorite.HTML import *
from cavorite import get_current_hash, t
try:
    import js
except ImportError:
    js = None


#TODO: There appear to be no unit tests for anything in this file. Please make them


class ContextMenu(div):
    # An improved context menu which can hopefully take care of collapsing itself
    def __init__(self, owner, posx, posy, menu_items, *args, **kwargs):
        self.owner = owner
        self.menu_items = menu_items
        self.posx = posx
        self.posy = posy
        super(ContextMenu, self).__init__({'onclick': self.owner.close_context_menu,
                                           'style': {'position': 'fixed',
                                                     'left': '0',
                                                     'top': '0',
                                                     'height': '100%',
                                                     'width': '100%',
                                                     'background-color': 'rgba(0, 0, 0, 0)',
                                                     'padding': '40px',
                                                     'z-index':'10001'}}, *args, **kwargs)

    def get_children(self):
        menu_items = [
                                li({'class': "context-menu__item"}, [
                                  a({'href': get_current_hash(), 'class': "context-menu__link", 'onclick': mi[1]}, [
                                    #i({'class': 'fa fa-eye'}),
                                    t(mi[0]),
                                  ]),
                                ]) for mi in self.menu_items]

        return [
                 nav({'class': "context-menu", 'style': 'left: {}px; top:{}px'.format(self.posx, self.posy)}, [
                   ul({'class': 'context-menu__items'}, menu_items),
                 ])
               ]

    @staticmethod
    def xy_from_e(e):
        if e.pageX or e.pageY:
            posx = e.pageX
            posy = e.pageY
        elif e.clientX or e.clientY:
            posx = e.clientX + js.globals.document.body.scrollLeft + \
                               js.globals.document.documentElement.scrollLeft
            posy = e.clientY + js.globals.document.body.scrollTop + \
                               js.globals.document.documentElement.scrollTop
        return posx, posy
