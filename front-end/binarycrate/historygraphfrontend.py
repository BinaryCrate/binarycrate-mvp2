# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function
import historygraph
from cavorite.ajaxget import ajaxget, ajaxpost
import json


documentcollection = None
documentcollection_download_ready = False
download_complete_callback = None

def initialise_document_collection(project_id, download_complete_callback_fn):
    documentcollection_download_ready = False
    global documentcollection
    documentcollection = historygraph.DocumentCollection()
    documentcollection.id = project_id

    global download_complete_callback
    download_complete_callback = download_complete_callback_fn

def historygraph_ajaxget_handler(xmlhttp, response):
    #print('historygraph_ajaxget_handler xmlhttp.responseText=', xmlhttp.responseText)
    #print('historygraph_ajaxget_handler response[history]=', response['history'])
    global documentcollection_download_ready
    global documentcollection
    documentcollection.load_from_json(str(xmlhttp.responseText))
    documentcollection_download_ready = True
    if download_complete_callback:
        download_complete_callback()

def download_document_collection():
    # Download the global document collection
    ajaxget('/api/historygraph/' + str(documentcollection.id) + '/', historygraph_ajaxget_handler)

def historygraph_ajaxpost_handler(xmlhttp, response):
    pass

def post_document_collection():
    import traceback
    #print('post_document_collection 1')
    global documentcollection
    #print('post_document_collection 2')
    #try:
    (historyedges, immutableobjects) = documentcollection.get_all_edges()
    #except:
    #    traceback.print_exc()
    #    return
    #print('post_document_collection 3')
    data = {"history":json.dumps(historyedges),"immutableobjects":json.dumps(immutableobjects)}
    #print('post_document_collection 4')
    #print('post_document_collection sending ', data)
    ajaxpost('/api/historygraph/' + str(documentcollection.id) + '/', data, historygraph_ajaxpost_handler)
    #print('post_document_collection 5')


