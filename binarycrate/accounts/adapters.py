# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
from allauth.account.adapter import DefaultAccountAdapter


class BCAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        # Override because we dont use the username field
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from allauth.account.utils import user_username, user_email, user_field
        first_name = user_field(user, 'first_name')
        last_name = user_field(user, 'last_name')
        email = user_email(user)
        user.email = request.POST['email']
        user.username = request.POST['email']


