# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 11:38:27
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-21 16:14:28

# generic imports
from sqlalchemy import Boolean, Column, ForeignKey, String, DateTime
from sqlalchemy import Integer

# custom imports
from database.database import Base


class TimePeriod(Base):
    __tablename__ = "TimePeriod"
    id = Column(Integer, primary_key=True, index=True)
    startDateTime = Column(DateTime)
    endDateTime = Column(DateTime)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())


class Organization(Base):
    __tablename__ = "Organization"
    id = Column(Integer, primary_key=True, index=True)
    href = Column(String)
    isHeadOffice = Column(Boolean)
    isLegalEntity = Column(Boolean)
    name = Column(String)
    nameType = Column(String)
    organizationType = Column(String)
    tradingName = Column(String)
    existsDuring = Column(Integer, ForeignKey("TimePeriod.id"))
    status = Column(String, default="initialized")
    _baseType = Column(String)
    _schemaLocation = Column(String)
    _type = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())


class Characteristic(Base):
    __tablename__ = "Characteristic"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    valueType = Column(String)
    value = Column(String, nullable=False)
    organization = Column(
        Integer,
        ForeignKey("Organization.id"),
        nullable=False
    )
    _baseType = Column(String)
    _schemaLocation = Column(String)
    _type = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return str(self.as_dict())
