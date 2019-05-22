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
from binarycrate.editor import BCPFile
from cavorite import t


def get_tree_important_nodes(tree):
    # This function exists because we want to get the versions of nodes after a mount_redraw
    #root_folder = tree.get_children()[0]
    #folder = root_folder.get_children()[0]
    #return root_folder, root_folder.get_children()[1], folder, folder.get_children()[2].get_children()[0]
    root_folder = tree.get_children()[0]
    hello_world = root_folder.folder_children[1]
    folder = root_folder.folder_children[0]
    hello_folder = folder.folder_children[0]
    return root_folder, hello_world, folder, hello_folder

def get_BCPFile_title(node):
    assert type(node) == BCPFile
    assert len(node.get_children()) == 1
    first_child = node.get_children()[0]
    assert first_child.get_tag_name().lower() == 'a'
    assert len(first_child.get_children()) == 1
    text_node = first_child.get_children()[0]
    assert type(text_node) == t
    return text_node.text
