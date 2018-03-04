# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from . import querysets

# Create your models here.

class HistoryEdge(models.Model):
    documentcollectionid = models.UUIDField()
    documentid = models.CharField(max_length=250)
    documentclassname = models.CharField(max_length=250)
    classname = models.CharField(max_length=250)
    endnodeid = models.CharField(max_length=250, primary_key=True)
    startnode1id = models.CharField(max_length=250)
    startnode2id = models.CharField(max_length=250)
    propertyownerid = models.CharField(max_length=250)
    propertyname = models.CharField(max_length=250)
    propertyvalue = models.CharField(max_length=250)
    propertytype = models.CharField(max_length=250)

    objects = querysets.HistoryEdgeQuerySet.as_manager()

