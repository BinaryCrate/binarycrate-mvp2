# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from binarycrate import BUILD_NUMBER

class TestBuilderNumber(object):
    def version_number(self):
        # Test the version is set and a six digit number
        build_number = BUILD_NUMBER
        assert len(build_number) == 6
        for ch in build_number:
            assert isdigit(ch)

