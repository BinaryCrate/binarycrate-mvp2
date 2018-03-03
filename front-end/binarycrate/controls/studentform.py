from __future__ import absolute_import, print_function
from cavorite.HTML import *
from cavorite.svg import svg
import copy


class StudentForm(object):
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
        assert self.file_location.startswith(python_module_dir)
        return self.file_location[len(python_module_dir):]


    def initialise_form_controls(self):
        self.form_controls = copy.deepcopy(self.get_form_items())
        for control in self.form_controls:
            setattr(self, control['name'], control)

    def get_form_controls(self):
        ret = list()
        html_controls = dict()
        for form_item in self.form_controls:
            print('initialise_form_controls form_item=', form_item)
            #TODO: Copied code from editor.py should be refactored
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
                #control = html_button({'style': style, 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption'])
            elif form_item['type'] == 'textbox':
                control_class = html_input
                attribs_extra = {'type': "text"}           
                #control = html_input({'type': "text", 'style': style, 'onmouseup': self.on_mouse_up, 'onmousedown': lambda e, form_item_id=form_item_id: self.select_new_item(form_item_id, e)}, form_item['caption'])
            elif form_item['type'] == 'image':
                control_class = img
                attribs_extra = { }           
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
        for form_item in self.form_controls:
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
                control = svg('line', {'x1': form_item['x'], 
                             'y1':form_item['y'],
                             'x2': form_item['x'] + form_item['width'],
                             'y2': form_item['y'] + form_item['height'],
                             'fill': form_item['fill'],
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

    def __init__(self, *args, **kwargs):
        super(StudentForm, self).__init__(*args, **kwargs)
        self.initialise_form_controls()


