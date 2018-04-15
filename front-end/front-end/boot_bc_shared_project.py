from __future__ import absolute_import, print_function

import binarycrate

print('Build number = ', binarycrate.BUILD_NUMBER)
print('Called boot_bc_shared_project.py')
binarycrate.start_shared_project()

