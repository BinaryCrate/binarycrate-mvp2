# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function


def IterateVirtualDOM(vnode, callback):
    # Iterate over the virtual DOM and call callback for every node
    callback(vnode)
    if hasattr(vnode, 'get_children'):
        for child in vnode.get_children():
            IterateVirtualDOM(child, callback)


def AnyVirtualDOM(vnode, callback):
    # Iterate over the virtual DOM and return True if callback returns True for any vnode
    # otherwise return false
    if callback(vnode):
        return True
    if hasattr(vnode, 'get_children'):
        for child in vnode.get_children():
            if AnyVirtualDOM(child, callback):
                return True
    return False

def get_matching_vnode(vnode, callback):
    # Iterate over vnode and all of it's children. Return the first node for which
    # callback returns true otherwise return None
    if callback(vnode):
        return vnode
    if hasattr(vnode, 'get_children'):
        for child in vnode.get_children():
            match = get_matching_vnode(child, callback)  
            if match is not None:
                return match
    return None

