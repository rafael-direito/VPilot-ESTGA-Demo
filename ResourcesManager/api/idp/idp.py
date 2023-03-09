# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-25 17:58:35
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-03-09 16:44:14

from fastapi_keycloak import FastAPIKeycloak
import os
import time
from idp.exceptions import IDPVariablesNotDefined

print(11)

MAX_LOOPS = 12

n_loops = 0
while True:
    n_loops += 1
    try:         
        print("Trying to connect to Keycloak Server...")   
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
        
        break
        
    except Exception as e:
        print(f"Impossible to connect to Keycloak Server. Exception: {e}")
        if n_loops == MAX_LOOPS:
            print("It was impossible to connect to Keycloak Server!")
            exit(1)
        print("Will try again in 10 seconds")
        time.sleep(10)