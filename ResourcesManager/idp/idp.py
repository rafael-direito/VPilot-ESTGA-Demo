# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-25 17:58:35
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-25 18:26:38

from fastapi_keycloak import FastAPIKeycloak
import os
from idp.exceptions import IDPVariablesNotDefined

server_url = os.environ.get('IDP_SERVER_URL')
client_id = os.environ.get('IDP_CLIENT_ID')
client_secret = os.environ.get('IDP_CLIENT_SECRET')
admin_client_secret = os.environ.get('IDP_ADMIN_CLIENT_SECRET')
realm = os.environ.get('IDP_REALM')
callback_uri = os.environ.get('IDP_CALLBACK_URI')

# Check if all required variables have been assigned
if not (server_url and client_id and client_secret and admin_client_secret
        and realm and callback_uri):
    raise IDPVariablesNotDefined(server_url, client_id, client_secret,
                                 admin_client_secret, realm, callback_uri)

# Establish IDP Connection
idp = FastAPIKeycloak(
    server_url=server_url,
    client_id=client_id,
    client_secret=client_secret,
    admin_client_secret=admin_client_secret,
    realm=realm,
    callback_uri=callback_uri
)
