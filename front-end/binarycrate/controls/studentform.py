from __future__ import absolute_import, print_function

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
            return de['form_items']


        
    def get_file_location(self):
        # Returns the file local relative to the module directory
        from binarycrate.editor import python_module_dir
        assert self.file_location.startswith(python_module_dir)
        return self.file_location[len(python_module_dir):]

