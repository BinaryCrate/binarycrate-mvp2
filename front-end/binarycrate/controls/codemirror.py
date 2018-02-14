from __future__ import absolute_import, print_function
from cavorite import c, t, Router, callbacks, timeouts
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy

class CodeMirrorHandlerVNode(textarea):
    def __init__(self, attribs=None, children=None, change_handler=None, **kwargs):
        #print('CodeMirrorHandlerVNode __init__ self=', self)
        attribs = copy.copy(attribs)
        attribs.update({'onchange': self.onchange_codemirror})
        self.change_handler = change_handler
        super(CodeMirrorHandlerVNode, self).__init__(attribs, children, **kwargs)

    def was_mounted(self):
        super(CodeMirrorHandlerVNode, self).was_mounted()
        timeouts.set_timeout(self.codemirror_init, 1)

    def codemirror_init(self):
        #print('CodeMirrorHandlerVNode codemirror_init self=', self)
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
        #print ('onchange_codemirror self.change_handler=', self.change_handler)
        #previewFrame = js.globals.document.getElementById('preview');
        #preview =  previewFrame.contentDocument or  previewFrame.contentWindow.document;
        #preview.open();
        content = self.editor.getValue()
        #preview.write(content);
        #preview.close();
        #print ('onchange_codemirror content=', content)
        if self.change_handler is not None:
            self.change_handler(content)



