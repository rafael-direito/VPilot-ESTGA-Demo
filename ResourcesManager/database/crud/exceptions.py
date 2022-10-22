# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 17:35:05
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-22 11:25:04

import logging

# Logger
logger = logging.getLogger(__name__)


class ImpossibleToCreateDatabaseEntry(Exception):

    def __init__(self, entity_type, entity_data=None, reason=None):
        self.entity_type = entity_type
        if entity_data and reason:
            self.entity_data = entity_data
            self.reason = reason
            self.message = f"Impossible to create a database entry for "\
                f"entity '{entity_type}' (entity_data='{str(entity_data)}', "\
                f"reason='{reason}'."
        else:
            self.message = f"Impossible to create a database entry for "\
                f"entity '{entity_type}'."
        logger.error(f"Exception: {self.message}")
        super().__init__(self.message)

    def __str__(self):
        return self.message


class EntityDoesNotExist(Exception):
    def __init__(self, entity_type, reason=None):
        self.entity_type = entity_type
        if reason:
            self.reason = reason
            self.message = f"Impossible to obtain entity ('{entity_type} ,"\
                f"reason='{reason}')."
        else:
            self.message = f"Impossible to obtain entity '{entity_type}'"
        logger.error(f"Exception: {self.message}")
        super().__init__(self.message)

    def __str__(self):
        return self.message
