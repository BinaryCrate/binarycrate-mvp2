from __future__ import unicode_literals, absolute_import, print_function
from cavorite.HTML import *


class UploadModal(object):
    def __init__(self, ownerview):
        self.ownerview = ownerview

    def get_modal_vnodes(self):
        # Return the vnodes to inject into the Virtual DOM to display the modal
        return       [
                      div({'onclick': self.ownerview.close_upload_modal, 'class': 'upload-files-modal-container'}, [
                        div({'class': 'upload-files-modal-content'}, [
                          html_button({'onclick': self.ownerview.close_upload_modal}, 'Close'),
                        ]),
                      ]),
                     ]


