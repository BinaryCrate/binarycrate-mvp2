from __future__ import absolute_import, unicode_literals, print_function
try:
    import js
except ImportError:
    js = None


def window_prompt(prompt):
    return js.globals.window.prompt(prompt)
