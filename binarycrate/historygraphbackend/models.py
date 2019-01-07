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

from django.db import models
from . import querysets

# Create your models here.

class HistoryEdge(models.Model):
    documentcollectionid = models.UUIDField()
    documentid = models.CharField(max_length=250, blank=True)
    documentclassname = models.CharField(max_length=250, blank=True)
    classname = models.CharField(max_length=250, blank=True)
    endnodeid = models.CharField(max_length=250, primary_key=True)
    startnode1id = models.CharField(max_length=250, blank=True)
    startnode2id = models.CharField(max_length=250, blank=True)
    propertyownerid = models.CharField(max_length=250, blank=True)
    propertyname = models.CharField(max_length=250, blank=True)
    propertyvalue = models.CharField(max_length=250, blank=True)
    propertytype = models.CharField(max_length=250, blank=True)
    nonce = models.CharField(max_length=250, blank=True)
    transaction_id = models.CharField(max_length=250, blank=True)

    objects = querysets.HistoryEdgeQuerySet.as_manager()
