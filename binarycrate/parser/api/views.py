# -*- coding: utf-8 -*-
# BinaryCrate -  BinaryCrate an in browser python IDE. Design to make learning coding easy.
# Copyright (C) 2018 BinaryCrate Pty Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import status
from redbaron import RedBaron
from .serializers import MemberFunctionsSerializer, AddMemberFunctionSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    #TODO: This class appears in multiple places remove or put in library
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

def process_prog(prog_text):
    red = RedBaron(prog_text)
    #classes = red.find_all("ClassNode")
    #assert len(classes) == 1, str(classes)
    #assert classes[0].parent == red, 'Class not in the global scope'
    #cls = classes[0]
    #fns = cls.find_all("DefNode")
    #if not any([fn.name == fn_name for fn in fns]):
    #    cls.append(fn_to_insert)
    return red

def get_class_name(red):
    # Return the name of the only class in the program test passed in which
    # is subclass of form
    classes = red.find_all("ClassNode")
    cls = classes[0]
    #print('get_class_name cls=', cls)
    #print('get_class_name dir(cls)=', dir(cls))
    #red.help()
    #print('----------------------------------------')
    #cls.inherit_from.help()
    #print('cls.inherit_from[0]', cls.inherit_from[0])
    #print('type(cls.inherit_from)', type(cls.inherit_from))
    #print('dir(cls.inherit_from)', dir(cls.inherit_from))
    #print('cls.inherit_from.node_list=', cls.inherit_from.node_list)
    #print('cls.inherit_from.node_list[0]=', cls.inherit_from.node_list[0])
    is_form_class = False
    try:
        for superclas in cls.inherit_from.node_list[0]:
            #print('Iterating superclas=', superclas)
            #print('type(superclas)=', type(superclas))
            #print('superclas.value=', superclas.value)
            is_form_class = is_form_class or superclas.value == 'Form'
    except TypeError:
        #print("Appears to not be iterable therefore there is only one superclass")
        superclas = cls.inherit_from.node_list[0]
        #print('superclas=', superclas)
        #print('type(superclas)=', type(superclas))
        #print('superclas.value=', superclas.value)
        is_form_class = is_form_class or superclas.value == 'Form'
    assert is_form_class
    return cls.name

def find_functions(red):
    classes = red.find_all("ClassNode")
    assert len(classes) == 1, str(classes)
    assert classes[0].parent == red, 'Class not in the global scope'
    cls = classes[0]
    fns = cls.find_all("DefNode")
    return [[fn.name, fn.absolute_bounding_box.top_left.line] for fn in fns]
    #fns = [fn for fn in fns if fn.name == fn_name]
    #assert len(fns) == 1, str(fns)
    #fn = fns[0]
    #assert fn.parent.parent == cls, fn.parent.parent.help()
    #print(dir(fn.absolute_bounding_box.top_left.line))
    #return fn.absolute_bounding_box.top_left.line

def add_function(red, fn_name, fn_text):
    classes = red.find_all("ClassNode")
    assert len(classes) == 1, str(classes)
    assert classes[0].parent == red, 'Class not in the global scope'
    cls = classes[0]
    fns = cls.find_all("DefNode")
    if not any([fn.name == fn_name for fn in fns]):
        cls.append(fn_text)
    return red.dumps()

class MemberFunctionsView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, format=None):
        serializer = MemberFunctionsSerializer(data=request.data)
        if serializer.is_valid():
            red = process_prog(serializer.data['content'])
            fns = find_functions(red)
            return Response({"classname": get_class_name(red),
                             "functions": fns}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddMemberFunctionView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, format=None):
        serializer = AddMemberFunctionSerializer(data=request.data)
        if serializer.is_valid():
            red = process_prog(serializer.data['content'])
            result = add_function(red, serializer.data['function_name'],
                                  serializer.data['newfunction'])
            fns = find_functions(red)
            return Response({'content': result, 'new_functions': fns,
                            "classname": get_class_name(red)},
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
