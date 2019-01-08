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
import historygraph
from cavorite.ajaxget import ajaxget, ajaxpost, ajaxdelete
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
    ajaxpost('/api/historygraph/' + str(documentcollection.id) + '/list/', [ ], historygraph_ajaxget_handler)

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
    ajaxpost('/api/historygraph/' + str(documentcollection.id) + '/write/', data, historygraph_ajaxpost_handler)
    #print('post_document_collection 5')

def delete_document_collection(project_id, callback):
    # Download the global document collection
    ajaxdelete('/api/historygraph/' + str(project_id) + '/', callback)
