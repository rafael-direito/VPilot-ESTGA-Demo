# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 17:35:05
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-25 18:23:50

import logging

# Logger
logger = logging.getLogger(__name__)


class IDPVariablesNotDefined(Exception):

    def __init__(self, idp_server_url, idp_client_id, idp_client_secret,
                 idp_admin_client_secret, idp_realm, idp_callback_uri):

        self.reason = "Not all IDP variables were configured. Impossible to "\
            "start an IDP connection."

        null_keys = [
            item[0].upper()
            for item
            in locals().items()
            if len(item) == 2
            and item[1] is None
        ]

        self.message = "To establish a connection with the IDP, the "\
            f"following variables can't be void: {null_keys}"

        logger.error(f"Exception: {self.message}")

        super().__init__(self.message)

    def __str__(self):
        return self.message
