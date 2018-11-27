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
from cavorite.HTML import *
from cavorite.svg import svg
import copy
from cavorite import Router, timeouts
from binarycrate.bcmunch import BCMunch
import uuid


class FormItemPropType(object):
    INT = 0
    STRING = 1
    BOOLEAN = 2
    COLOR = 3
    PRELOADED_IMAGE = 4

def get_form_item_property(form_item_type):
    if form_item_type == 'line':
        return  {'x1': FormItemPropType.INT,
                 'y1': FormItemPropType.INT,
                 'x2': FormItemPropType.INT,
                 'y2': FormItemPropType.INT,
                 'name': FormItemPropType.STRING,
                 'stroke_width': FormItemPropType.INT,
                 'stroke': FormItemPropType.COLOR,
                 'visible': FormItemPropType.BOOLEAN}
    props = {'x': FormItemPropType.INT,
             'y': FormItemPropType.INT,
             'width': FormItemPropType.INT,
             'height': FormItemPropType.INT,
             'name': FormItemPropType.STRING,
             'visible': FormItemPropType.BOOLEAN}
    if form_item_type == 'button' or form_item_type == 'label' \
       or form_item_type == 'frame' or form_item_type == 'checkbox':
        props.update({'caption': FormItemPropType.STRING})
    if form_item_type == 'textbox':
        props.update({'text': FormItemPropType.STRING})
    if form_item_type == 'image':
        props.update({'src': FormItemPropType.STRING, 'preloaded_image': FormItemPropType.PRELOADED_IMAGE})
    if form_item_type == 'checkbox':
        props.update({'value': FormItemPropType.BOOLEAN})
    if form_item_type in {'rect', 'circle', 'ellipse', 'hexagon'}:
        props.update({'stroke_width': FormItemPropType.INT,
                      'stroke': FormItemPropType.COLOR,
                      'fill': FormItemPropType.COLOR,
                     })
    return props

def get_form_item_optional_members(form_item_type):
    #print('get_form_item_optional_members form_item_type=',form_item_type)
    #assert False
    #Optional members can only every be created dynamically
    if form_item_type == 'button':
        return ['onclick']
    return []

control_types = ['line', 'button', 'label', 'frame','checkbox',
                 'textbox', 'image', 'checkbox', 'rect',
                 'circle', 'ellipse', 'hexagon',
                ]

# Dynamically create classes from https://stackoverflow.com/a/15247892
def ClassFactory(class_name, control_type, BaseClass):
    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)
        self.type = control_type
        if 'id' not in self:
            self.id = str(uuid.uuid4())
    newclass = type(str(class_name), (BaseClass,),{"__init__": __init__,
        "_members": get_form_item_property(control_type).keys(),
        "_optional_members": get_form_item_optional_members(control_type)})
    return newclass

control_types2 = dict()

# Dynamically insert variables into the global namespace
for control_type in control_types:
    class_name = control_type[0].upper() + control_type[1:]
    cls = ClassFactory(class_name, control_type, BCMunch)
    globals()[class_name] = cls
    control_types2[control_type] = cls


class Form(object):
    def get_form_items(self, loc=None, parent_id=None):
        from binarycrate.editor import project
        # Return the form items for this form
        if loc is None:
            loc = self.get_file_location()
        if parent_id is None:
            de = [de for de in project['directory_entry'] if de['parent_id'] is None][0]
            parent_id = de['id']
        i = loc.find('/')
        if i > 0:
            # This is directory
            dir_name = loc[:i]
            rest = loc[i + 1:]
            de = [de for de in project['directory_entry'] if de['parent_id'] == parent_id and de['name'] == dir_name][0]
            return self.get_form_items(rest, de['id'])
        else:
            de = [de for de in project['directory_entry'] if de['parent_id'] == parent_id and de['name'] == loc][0]
            #print('get_form_items returning=', de['form_items'])
            #print('get_form_items type returning=', type(de['form_items']))
            return de['form_items']



    def get_file_location(self):
        # Returns the file local relative to the module directory
        from binarycrate.editor import python_module_dir
        #print('python_module_dir=', python_module_dir)
        #print('self.file_location=', self.file_location)
        assert self.file_location.startswith(python_module_dir)
        return self.file_location[len(python_module_dir):]


    def initialise_form_controls(self):
        #print("initialise_form_controls fis=", [fi for fi in
        #                      self.get_form_items()])
        #self._static_form_controls = []
        #print('initialise_form_controls self.get_form_items()=', self.get_form_items())
        #print('initialise_form_controls control_types2=', control_types2)
        self._static_form_controls = [control_types2[fi['type']](fi) for fi in
                              self.get_form_items() if fi['type'] in control_types2]
        self._dynamic_form_controls = []
        for control in self._static_form_controls:
            setattr(self, control['name'], control)

    def get_form_controls(self):
        #print('get_form_controls self._dynamic_form_controls=', self._dynamic_form_controls)
        return self._static_form_controls + self._dynamic_form_controls

    def add_control(self, control):
        #print('add_control control=', control)
        self._dynamic_form_controls.append(control)

    def remove_dynamic_controls(self):
        self._dynamic_form_controls = []

    def remove_dynamic_control(self, control):
        self._dynamic_form_controls.remove(control)

    def handle_onclick(self, e, form_item_name):
        #print('handle_onclick form_item_name=', form_item_name)
        if hasattr(self, form_item_name + '_onclick'):
            #print('handle_onclick calling custom handler')
            getattr(self, form_item_name + '_onclick')(e)
        self.editorview.mount_redraw()
        Router.router.ResetHashChange()

    def get_form_control_elements(self):
        ret = list()
        html_controls = dict()
        control = None
        for form_item in self.get_form_controls():
            if form_item['visible'] == False:
                # Don't write invisible items out the DOM
                continue
            #print('initialise_form_controls form_item=', form_item)
            #TODO: Copied code from editor.py should be refactored
            if form_item['type'] == 'line':
                style = ''.join(('position: absolute; ',
                                'z-index: 1; ',
                                'left: {};'.format(form_item['x1']),
                                'top: {};'.format(form_item['y1']),
                                'width: {};'.format(form_item['x2'] - form_item['x1']),
                                'height: {};'.format(form_item['x2'] - form_item['x1'])
                                ))
            else:
                style = ''.join(('position: absolute; ',
                                'z-index: 1; ',
                                'left: {};'.format(form_item['x']),
                                'top: {};'.format(form_item['y']),
                                'width: {};'.format(form_item['width']),
                                'height: {};'.format(form_item['height'])
                                ))
            #print('get_selected_de_form_controls form_item[id]=',form_item['id'])
            form_item_id = form_item['id']
            attribs = {'style': style
                       }
            attribs_extra = { }
            control_class = None
            if form_item['type'] == 'button':
                control_class = html_button
                if form_item in self._static_form_controls:
                    # Static control fire handle_onclick to route then dynamic ones may have their own handler attached
                    attribs_extra = { 'onclick': lambda e, form_item_name=form_item['name']: self.handle_onclick(e, form_item_name) }
                else:
                    attribs_extra = { 'onclick': form_item.get('onclick', lambda e: None) }
                #control = html_button({'style': style, 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption'])
            elif form_item['type'] == 'textbox':
                control_class = html_input
                attribs_extra = {'type': "text"}
                #control = html_input({'type': "text", 'style': style, 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption'])
            elif form_item['type'] == 'image':
                control_class = img
                project = self.editorview.get_project()
                preloaded_image = form_item['preloaded_image']
                if preloaded_image != '':
                    image = filter(lambda image: image['id'] == preloaded_image, self.images)[0]
                    i = image['name'].rfind('.')
                    extension = image['name'][i:]
                    attribs_extra = {'src': '/images/images-{0}/{1}{2}'.format(project['id'],
                                     image['id'], extension),
                                     'preloaded_image': preloaded_image }
                #attribs_extra = { 'src': 'text', 'preloaded_image': '' }
            elif form_item['type'] == 'label':
                control_class = p
                attribs_extra = { }
            elif form_item['type'] == 'frame':
                control_class = div
                #attribs_extra = {'s': "text"}
            elif form_item['type'] == 'checkbox':
                control_class = html_input
                attribs_extra = merge_dicts({'type': "checkbox", 'form_item': 'True'}, {'checked': 'checked'} if form_item['value'] else { })
            elif form_item['type'] == 'select':
                control_class = select
                attribs_extra = { }
            attribs.update(attribs_extra)
            if  control_class:
                control = control_class(attribs, form_item.get('caption', ''))
                html_controls[form_item['name']] = control
                ret.append(control)
        svg_list = list()
        for form_item in self.get_form_controls():
            if form_item['type'] == 'rect':
                control = svg('rect', {'x': form_item['x'],
                             'y':form_item['y'],
                             'width': form_item['width'],
                             'height': form_item['height'],
                             'fill': form_item['fill'],
                             'stroke-width':  form_item['stroke_width'],
                             'stroke': form_item['stroke'],
                             #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)", 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item['id']: self.select_new_item(form_item_id, e), 'oncontextmenu': lambda e, form_item_id=form_item['id']: self.contextmenu_control(form_item_id, e)}))
                             })
            if form_item['type'] == 'circle':
                control = svg('circle', {'cx': form_item['x'] + form_item['width'] / 2,
                             'cy':form_item['y'] + form_item['height'] / 2,
                             'r': form_item['width'] / 2,
                             #'height': form_item['height'],
                             'fill': form_item['fill'],
                             'stroke-width':  form_item['stroke_width'],
                             'stroke': form_item['stroke'],
                             #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)",
                             })
            if form_item['type'] == 'ellipse':
                control = svg('ellipse', {'cx': form_item['x'] + form_item['width'] / 2,
                             'cy':form_item['y'] + form_item['height'] / 2,
                             'rx': form_item['width'] / 2,
                             'ry': form_item['height'] / 2,
                             'fill': form_item['fill'],
                             'stroke-width':  form_item['stroke_width'],
                             'stroke': form_item['stroke'],
                             #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)",
                             })
            if form_item['type'] == 'line':
                control = svg('line', {'x1': form_item['x1'],
                             'y1':form_item['y1'],
                             'x2': form_item['x2'],
                             'y2': form_item['y2'],
                             #'fill': form_item['fill'],
                             'stroke-width':  form_item['stroke_width'],
                             'stroke': form_item['stroke'],
                             #'style':"fill:None;stroke-width:5;stroke:rgb(0,255,0)",
                             })
            if form_item['type'] == 'hexagon':
                # Draw a hexagon
                x1 = form_item['x'] + form_item['width'] / 2
                y1 = form_item['y']
                x2 = form_item['x'] + form_item['width']
                y2 = form_item['y'] + form_item['height'] / 4
                x3 = form_item['x'] + form_item['width']
                y3 = form_item['y'] + form_item['height'] * 3 / 4
                x4 = form_item['x'] + form_item['width'] / 2
                y4 = form_item['y']+ form_item['height']
                x5 = form_item['x']
                y5 = form_item['y'] + form_item['height'] * 3 / 4
                x6 = form_item['x']
                y6 = form_item['y'] + form_item['height'] / 4
                points = '{},{} {},{} {},{} {},{} {},{} {},{}'.format(x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6)
                control = svg('polygon', {'points': points,
                             'fill': form_item['fill'],
                             'stroke-width':  form_item['stroke_width'],
                             'stroke': form_item['stroke']})
            if control is not None:
                svg_list.append(control)
                html_controls[form_item['name']] = control

        ret.append(svg('svg', {'id': 'preview-svg', 'height': '100%', 'width': '100%'}, svg_list))
        return ret

    def __init__(self, parent=None, *args, **kwargs):
        assert bool('editorview' in kwargs) != bool(parent is not None), 'A form must set either a parent or the editorview'
        self.editorview = kwargs.pop('editorview', None)
        self.parent = parent
        if parent is not None:
            self.parent = parent
            self.editorview = self.parent.editorview
            self.editorview.form_stack.append(self)
        self.images = self.editorview.images
        self._active_timeouts = set()
        self._active_intervals = set()
        super(Form, self).__init__(*args, **kwargs)
        self.initialise_form_controls()

    def on_historygraph_download_complete(self):
        pass

    def on_child_form_closed(self):
        pass

    def close(self):
        self.editorview.form_stack = self.editorview.form_stack[:-1]
        if self.parent is not None:
            self.parent.on_child_form_closed()

    def set_timeout(self, func, delay):
        # We need a list here because we need a variable the we can amend and
        # access from inside the inner function.
        value_wrapper = list()
        def wrapper():
            func()
            self._active_timeouts.remove(value_wrapper[0])
            self.editorview.mount_redraw()
            Router.router.ResetHashChange()
        value_wrapper.append(timeouts.set_timeout(wrapper, delay))
        self._active_timeouts.add(value_wrapper[0])
        return value_wrapper[0]

    def clear_all_active_timeouts(self):
        timeouts = copy.copy(self._active_timeouts)
        for val in timeouts:
            self.clear_timeout(val)

    def clear_timeout(self, val):
        self._active_timeouts.remove(val)
        timeouts.clear_timeout(val)

    def set_interval(self, func, delay):
        def wrapper():
            func()
            self.editorview.mount_redraw()
            Router.router.ResetHashChange()
        val = timeouts.set_interval(wrapper, delay)
        self._active_intervals.add(val)
        return val

    def clear_all_active_intervals(self):
        intervals = copy.copy(self._active_intervals)
        for val in intervals:
            self.clear_interval(val)

    def clear_interval(self, val):
        self._active_intervals.remove(val)
        timeouts.clear_interval(val)

    def get_preloaded_images(self):
        return self.editorview.images

    def get_preloaded_image_id(self, image_name):
        images = [image for image in self.get_preloaded_images() if image['name'] == image_name]
        assert len(images) == 1, 'No image matches that name'
        return images[0]['id']

    def on_body_click(self):
        pass

    def on_body_mousemove(self, x, y):
        pass
