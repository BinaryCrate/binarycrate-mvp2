# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import historygraph
from cavorite.ajaxget import ajaxget, ajaxpost
import json


documentcollection = None
documentcollection_download_ready = False

def initialise_document_collection(project_id):
    documentcollection_download_ready = False
    global documentcollection
    documentcollection = historygraph.DocumentCollection()
    documentcollection.id = project_id

def historygraph_ajaxget_handler(xmlhttp, response):
    global documentcollection_download_ready
    global documentcollection
    documentcollection.LoadFromJSON(json.dumps({'history': response, 'immutableobjects': []}))
    documentcollection_download_ready = True

def download_document_collection():
    # Download the global document collection
    ajaxget('/api/historygraph/' + str(documentcollection.id) + '/', historygraph_ajaxget_handler)

def historygraph_ajaxpost_handler(xmlhttp, response):
    pass

def post_document_collection():
    global documentcollection
    (historyedges, immutableobjects) = documentcollection.getAllEdges()
    ajaxpost('/api/historygraph/' + str(documentcollection.id) + '/', historyedges, historygraph_ajaxpost_handler)


