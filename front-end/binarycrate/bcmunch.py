#-*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from munch import *

class BCMunch(Munch):
    def __init__(self, *args, **kwargs):
        super(BCMunch, self).__init__(*args, **kwargs)
        #print('self._members=', set(self._members))
        #print('self.keys()=', set(self.keys()))
        assert set(self._members)  == set(self.keys()) - {'id', 'type'}