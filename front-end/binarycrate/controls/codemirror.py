from __future__ import absolute_import, print_function
from cavorite import c, t, Router, callbacks, timeouts
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy

class CodeMirrorHandlerVNode(textarea):
    def __init__(self, attribs=None, children=None, cssClass=None, **kwargs):
        attribs = copy.copy(attribs)
        attribs.update({'onchange': self.onchange_codemirror})
        super(CodeMirrorHandlerVNode, self).__init__(attribs, children, cssClass=cssClass, **kwargs)

    def was_mounted(self):
        super(CodeMirrorHandlerVNode, self).was_mounted()
        timeouts.set_timeout(self.codemirror_init, 1)

    def codemirror_init(self):
        textarea = js.globals.document.getElementById("code")
        self.editor = js.globals.CodeMirror.fromTextArea(textarea, {
            'lineNumbers': True,
            'mode': 'text/html',
            #'mode': 'python',
            'viewportMargin': js.globals.Infinity,
          })

        @js.Function
        def change_callback_handler(a, b):
            callbacks.global_callbacks['onchange'][str(textarea.getAttribute('_cavorite_id'))](self.editor)

        self.editor.on('change', change_callback_handler)

        self.onchange_codemirror(None)

    def onchange_codemirror(self, e):
        previewFrame = js.globals.document.getElementById('preview');
        preview =  previewFrame.contentDocument or  previewFrame.contentWindow.document;
        preview.open();
        preview.write(self.editor.getValue());
        preview.close();



