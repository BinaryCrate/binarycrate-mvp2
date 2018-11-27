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


def get_matching_vnodes(vnode, callback):
    # Iterate over vnode and all of it's children. Return the first node for which
    # callback returns true otherwise return None
    ret = list()
    if callback(vnode):
        ret.append(vnode)
    if hasattr(vnode, 'get_children'):
        children = vnode.get_children()
        if children is not None:
            for child in children:
                ret.extend(get_matching_vnodes(child, callback))
    return ret

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

def get_vnode_by_css_class(vnode, css_class):
    return get_matching_vnode(vnode, lambda n: hasattr(n, 'get_attribs') and n.get_attribs().get('class') == css_class)
