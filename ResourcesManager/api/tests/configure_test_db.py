# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2022-10-17 22:45:02
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2022-10-28 16:29:19

# general imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# custom imports
from main import app, get_db
from routers import organizations_router

engine = create_engine(
    url="sqlite:///./test.db",
    connect_args={
        "check_same_thread": False
    }
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[organizations_router.get_db] = override_get_db
test_client = TestClient(app)
