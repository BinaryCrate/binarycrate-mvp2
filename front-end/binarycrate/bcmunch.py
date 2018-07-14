#-*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from munch import *

class BCMunch(Munch):
    _optional_members = []

    def __init__(self, *args, **kwargs):
        super(BCMunch, self).__init__(*args, **kwargs)
        #print('self._members=', set(self._members))
        #print('self.keys()=', set(self.keys()))
        #print('self._optional_members=', set(self._optional_members))
        assert set(self._members)  == set(self.keys()) - {'id', 'type'} - \
            set(self._optional_members)
