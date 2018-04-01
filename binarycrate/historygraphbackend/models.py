# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

    objects = querysets.HistoryEdgeQuerySet.as_manager()

