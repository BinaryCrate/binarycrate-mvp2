from __future__ import absolute_import, print_function
from cavorite import c, t, Router, callbacks, timeouts, lazy_eval
from cavorite.HTML import *
try:
    import js
except ImportError:
    js = None
import copy

global_editor = None
global_textarea = None
global_change_callback_handler = None
global_on_tab = None

def initialise_codemirror_callbacks():
    @js.Function
    def change_callback_handler(a, b):
        callbacks.global_callbacks['onchange'][str(global_textarea.getAttribute('_cavorite_id'))](global_editor)

    global global_change_callback_handler
    global_change_callback_handler = change_callback_handler

    @js.Function
    def on_tab(cm):
        if cm.somethingSelected():
            sel = global_editor.getSelection("\n");
            # Indent only if there are multiple lines selected, or if the selection spans a full line
            if (sel.length > 0 and (sel.indexOf("\n") > -1 or sel.length == cm.getLine(cm.getCursor().line).length)):
                cm.indentSelection("add")
                return

        if cm.options.indentWithTabs:
            cm.execCommand("insertTab")
        else:
            cm.execCommand("insertSoftTab")

    global global_on_tab
    global_on_tab = on_tab

last_selection = 'lastsel'

class CodeMirrorHandlerVNode(textarea):
    def __init__(self, attribs=None, children=None, change_handler=None,
                 read_only=False, current_selection_fn=None, **kwargs):
        attribs = copy.copy(attribs)
        attribs.update({'onchange': self.onchange_codemirror})
        self.change_handler = change_handler
        self.editor = None
        self.waiting_for_timeout = False
        self.read_only = read_only
        self.current_selection_fn = current_selection_fn
        super(CodeMirrorHandlerVNode, self).__init__(attribs, children, **kwargs)

    def was_mounted(self):
        #print("CodeMirrorHandlerVNode was_mounted called")
        super(CodeMirrorHandlerVNode, self).was_mounted()
        #should_init = True
        global last_selection
        should_init = last_selection != self.current_selection_fn()
        last_selection = self.current_selection_fn()
        #print("CodeMirrorHandlerVNode was_mounted  last_selection=", last_selection)
        #print("CodeMirrorHandlerVNode was_mounted  should_init=", should_init)
        if should_init:
            #should_init = js.globals.document.getElementsByClassName('CodeMirror').length < 2
            code_mirrors = js.globals.document.getElementsByClassName('CodeMirror')
            #print('CodeMirror was_mounted self.editor=', self.editor)
            #if self.editor is not None:
            #    self.editor.parentNode.removeChild(self.editor);
            js.globals.code_mirrors = code_mirrors

            #print('was_mounted code_mirrors=', code_mirrors)
            to_delete = []
            for i in range(code_mirrors.length):
                #print('code_mirrors[i].tagName=', code_mirrors[i].tagName)
                if str(code_mirrors[i].tagName) == "DIV":
                    to_delete.append(code_mirrors[i])

            #while code_mirrors.length > 1:
            #    code_mirrors.item(1).parentNode.removeChild(code_mirrors.item(1));
            for div in to_delete:
                div.parentNode.removeChild(div);



            #print("CodeMirrorHandlerVNode should_init=", should_init)
            textarea = js.globals.document.getElementById("code")
            read_only = lazy_eval(self.read_only)
            self.editor = js.globals.CodeMirror.fromTextArea(textarea, {
                'lineNumbers': True,
                #'mode': 'text/html',
                'mode': 'python',
                'indentUnit': 4,
                'viewportMargin': js.globals.Infinity,
                'readOnly': read_only,
              })
            self.editor.addKeyMap({'Tab': global_on_tab,})

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
        #preview =  previewFrame.contentDocument or  previewFrame.contentWindow.document; #don't need preview if python
        #preview.open();
        content = self.editor.getValue()
        #preview.write(content);
        #preview.close();
        #print ('onchange_codemirror content=', content)
        if self.change_handler is not None:
            self.change_handler(content)
        #e.stopPropagation()
        #e.preventDefault()
