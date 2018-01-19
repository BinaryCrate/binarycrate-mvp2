# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Permission is only allowed to the owner of the object
        return obj.owner == request.user
