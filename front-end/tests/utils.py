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


def style_to_dict(style_str):
    # style_str = an inline style as a string
    l = style_str.split(';')
    l = [s for s in l if s != '']
    def remove_quotes(s):
        if s == '' or s == '"' or s == "'":
            return ''
        if (s[0] == "'" and s[-1] == "'") or (s[0] == '"' and s[-1] == '"'):
            return s[1:-1]
        return s
    l = [(s[:s.find(':')].strip(), remove_quotes(s[s.find(':') + 1:]).strip()) for s in l]
    ret = {s[0]: s[1] for s in l}
    return ret

def get_vnode_by_id(vnode, id):
    return get_matching_vnode(vnode, lambda n: hasattr(n, 'get_attribs') and n.get_attribs().get('id') == id)


