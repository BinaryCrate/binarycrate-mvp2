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
from .models import HistoryEdge
from historygraph import DocumentCollection
from json import JSONEncoder
import copy
from collections import defaultdict


def get_start_node1(e):
    return e._start_hashes[0]

def get_start_node2(e):
    return start_hashes[1] if len(e._start_hashes) > 1 else ""

def get_unknown_edges(documentcollectionid, known_endnodes):
    def historyedges_to_dict(e):
        return {'documentid': e.documentid,
            'documentclassname': e.documentclassname,
            'classname': e.__class__.__name__,
            'endnodeid': e.endnodeid,
            'startnode1id':e.startnode1id,
            'startnode2id': e.startnode2id,
            'propertyownerid': e.propertyownerid,
            'propertyname': e.propertyname,
            'propertyvalue': e.propertyvalue,
            'propertytype': e.propertytype,
            'nonce': e.nonce,
            'transaction_id': e.transaction_id,
            'documentcollectionid': documentcollectionid}
    """def historyedges_to_tuple(e):
        return (e.documentid,
            e.documentclassname,
            e.classname,
            e.endnodeid,
            e.startnode1id,
            e.startnode2id,
            e.propertyownerid,
            e.propertyname,
            e.propertyvalue,
            e.propertytype,
            e.nonce,
            e.transaction_id)"""

    def get_past_edges(edge_dict):
        start_edge = [e for e in edge_dict.values() if e.startnode1id == ""
                      ][0].endnodeid
        past_edges = defaultdict(set)

        def _get_past_edges(current):
            edge = edge_dict[current]
            next_edges = [e for e in edge_dict.values() if
                          e.startnode1id == current or
                          e.startnode2id == current]
            for e in next_edges:
                past_edges[e.endnodeid].add(current)
            for e in next_edges:
                _get_past_edges(e.endnodeid)

        _get_past_edges(start_edge)
        return past_edges

    ret = list()
    known_documents = set(known_endnodes.keys())
    # Return all of the edges for any document the client does not know about
    # This assumes the client does not know about these documents
    unknown_document_edges = HistoryEdge.objects.exclude(
        documentid__in=known_documents).filter(
            documentcollectionid=documentcollectionid)
    #print('known_documents=', known_documents)
    #print('documentcollectionid=', documentcollectionid)
    #print('unknown_document_edges=', [(e.documentid, e.documentcollectionid) for e in unknown_document_edges])
    future_edges = list()
    for k, v in known_endnodes.iteritems():
        # Iterate over each known document seperately
        known_document_edges = HistoryEdge.objects.filter(
            documentid=k).all()
        # Build a map of the endnodeid to the known edge this will be faster
        # than using the ORM queries
        edge_dict = {e.endnodeid: e for e in known_document_edges}
        # Build the past edges dictionaries
        past_edges = get_past_edges(edge_dict)
        # An edge is in the future if we are in it's past
        # k = the id of the document we are interested in
        # v = the the last known edge hash from the client
        # k2 = the endnodeid of an edge
        # v2 = the set of all edges in the past of k2
        # if v is in v2 then k2 is in v's future
        future_edges.extend([k2 for k2, v2 in past_edges.iteritems()
                             if v in v2])

    return list(unknown_document_edges) + \
        list(HistoryEdge.objects.filter(endnodeid__in=future_edges))
