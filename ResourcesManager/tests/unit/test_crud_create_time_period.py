# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 21:13:44
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-17 23:34:14

# general imports
import pytest
from pydantic import ValidationError
import datetime

# custom imports
from database.crud import crud
import schemas.tmf632_party_mgmt as TMF632Schemas
from tests.configure_test_db import override_get_db
from tests.configure_test_db import engine
from database.database import Base


# Create the DB before each test and delete it afterwards
@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# Tests
def test_time_period_correct_database_creation_both_dates():

    database = next(override_get_db())

    time_period = TMF632Schemas.TimePeriod(
        startDateTime="2015-10-22T08:31:52.026Z",
        endDateTime="2016-10-22T08:31:52.026Z",
    )

    result = crud.create_time_period(
        db=database,
        time_period=time_period
    )

    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)
    endDateTime = datetime.datetime(2016, 10, 22, 8, 31, 52, 26000)

    assert result.startDateTime.replace(tzinfo=None) == startDateTime
    assert result.endDateTime.replace(tzinfo=None) == endDateTime


def test_time_period_correct_database_creation_only_1_date():

    database = next(override_get_db())

    time_period = TMF632Schemas.TimePeriod(
        startDateTime="2015-10-22T08:31:52.026Z",
    )

    result = crud.create_time_period(
        db=database,
        time_period=time_period
    )

    startDateTime = datetime.datetime(2015, 10, 22, 8, 31, 52, 26000)

    assert result.startDateTime.replace(tzinfo=None) == startDateTime
    assert result.endDateTime is None


def test_time_period_incorrect_data():

    with pytest.raises(ValidationError) as exception:
        TMF632Schemas.TimePeriod(
            startDateTime="This 'date' is not a date!",
        )

    assert "TimePeriod" and "startDateTime" in str(exception)
