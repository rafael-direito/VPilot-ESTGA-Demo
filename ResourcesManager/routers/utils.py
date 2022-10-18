# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 17:21:10
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-17 21:19:05

from http import HTTPStatus
from fastapi.responses import JSONResponse
from typing import Any


def compose_error_payload(code: str, reason: str, message: str = None,
                          status: str = None, reference_error: str = None,
                          base_type: str = None, schema_location: str = None,
                          type: str = None):

    payload = {
        "code": code,
        "reason": reason,
    }

    if message:
        payload["message"] = message
    if status:
        payload["status"] = message
    if reference_error:
        payload["referenceError"] = message
    if message:
        payload["message"] = message
    if base_type:
        payload["@baseType"] = message
    if schema_location:
        payload["@schemaLocation"] = message
    if type:
        payload["@type"] = message

    return payload


def create_http_response(http_status: HTTPStatus = HTTPStatus.OK,
                         content: Any = {}):
    return JSONResponse(
        status_code=http_status.value,
        content=content,
        # headers={"Access-Control-Allow-Origin": "*"}
        )
