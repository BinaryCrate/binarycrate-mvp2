# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function


def IterateVirtualDOM(vnode, callback):
    callback(vnode)
    if hasattr(vnode, 'get_children'):
        for child in vnode.get_children():
            IterateVirtualDOM(child, callback)

