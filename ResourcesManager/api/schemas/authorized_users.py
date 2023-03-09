# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-29 16:10:11
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-29 16:18:03

from __future__ import annotations

from typing import Any, List
from pydantic import BaseModel, Field


class NonNullModel(BaseModel):

    def dict(self, *args, **kwargs):
        if kwargs and kwargs.get("exclude_none") is not None:
            kwargs["exclude_none"] = True
            return BaseModel.dict(self, *args, **kwargs)


class Model(BaseModel):
    __root__: Any


class AnyModel(BaseModel):
    __root__: Any


class AuthorizedUser(BaseModel):
    user_id: str = Field(None, description='Id of the User')


class OrganizationAuthorizedUsers(BaseModel):
    organization_id: str = Field(
        ...,
        description='Unique-Identifier for the organization'
    )
    authorized_users: List[AuthorizedUser] = Field(
        None, description='List of Authorized Users'
    )
