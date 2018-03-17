from __future__ import absolute_import, print_function
from cavorite import c, t, Router, callbacks, timeouts
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy

global_editor = None
global_textarea = None
global_change_callback_handler = None

def initialise_codemirror_callbacks():
    @js.Function
    def change_callback_handler(a, b):
        #print('change_callback_handler2 called a=',a)
        #print('change_callback_handler2 called b=',b)
        #print('change_callback_handler2 called type(a)=',type(a))
        #print('change_callback_handler2 called type(b)=',type(b))
        #print('change_callback_handler2 called dir(a)=',dir(a))
        #print('change_callback_handler2 called dir(b)=',dir(b))
        #print('change_callback_handler2 called a=global_editor',a == global_editor)
        callbacks.global_callbacks['onchange'][str(global_textarea.getAttribute('_cavorite_id'))](global_editor)

    global global_change_callback_handler
    global_change_callback_handler = change_callback_handler

class CodeMirrorHandlerVNode(textarea):
    def __init__(self, attribs=None, children=None, change_handler=None, **kwargs):
        #print('CodeMirrorHandlerVNode __init__ self=', self)
        attribs = copy.copy(attribs)
        attribs.update({'onchange': self.onchange_codemirror})
        self.change_handler = change_handler
        self.editor = None
        self.waiting_for_timeout = False
        super(CodeMirrorHandlerVNode, self).__init__(attribs, children, **kwargs)

    def was_mounted(self):
        super(CodeMirrorHandlerVNode, self).was_mounted()
        should_init = True
        #print('CodeMirrorHandlerVNode was_mounted called should_init=',should_init)
        #if self.editor is not None:
        #print('CodeMirrorHandlerVNode contains=', js.globals.document.getElementsByClassName('CodeMirror').length)
        should_init = js.globals.document.getElementsByClassName('CodeMirror').length < 2
        if should_init:
        #if  self.waiting_for_timeout == False:
        #    self.waiting_for_timeout = True
        #    timeouts.set_timeout(self.codemirror_init, 1)
            textarea = js.globals.document.getElementById("code")
            self.editor = js.globals.CodeMirror.fromTextArea(textarea, {
                'lineNumbers': True,
                'mode': 'text/html',
                #'mode': 'python',
                'viewportMargin': js.globals.Infinity,
              })

            #@js.Function
            #def change_callback_handler(a, b):
            #    #print('change_callback_handler called')
            #    callbacks.global_callbacks['onchange'][str(textarea.getAttribute('_cavorite_id'))](self.editor)
            assert global_change_callback_handler, 'CodeMirror global_change_callback_handler not set'
            self.editor.on('change', global_change_callback_handler)

            global global_editor
            global_editor = self.editor
            global global_textarea
            global_textarea = textarea
            #self.onchange_codemirror(None)

    """
    def codemirror_init(self):
        self.waiting_for_timeout = False
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
            print('change_callback_handler called')
            callbacks.global_callbacks['onchange'][str(textarea.getAttribute('_cavorite_id'))](self.editor)

        self.editor.on('change', change_callback_handler2)

        self.onchange_codemirror(None)
    """

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
        #e.stopPropagation()
        #e.preventDefault()



