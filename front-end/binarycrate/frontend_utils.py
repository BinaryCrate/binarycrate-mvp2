from __future__ import unicode_literals, absolute_import, print_function
try:
    import js
except ImportError:
    js = None

def get_controls_height():
    return int(js.globals.window.innerHeight) - 50 - 56 - 8

def get_controls_width():
    return int(js.globals.window.innerWidth) - 150 - 20
