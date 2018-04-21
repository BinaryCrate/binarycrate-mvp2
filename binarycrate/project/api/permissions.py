# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from rest_framework import permissions


class IsReadOnlyOrAuthenticated(permissions.IsAuthenticated):
    """
    Object-level permission to only allow read-only operations if unless authenticated
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return super(IsReadOnlyOrAuthenticated, self).has_permission(request, view)



