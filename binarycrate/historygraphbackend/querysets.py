# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class HistoryEdgeQuerySet(models.query.QuerySet):
    def by_document_collection_id(self, dcid):
        return self.filter(documentcollectionid=dcid)

    def by_endnodeid(self, endnodeid):
        return self.filter(endnodeid=endnodeid)
