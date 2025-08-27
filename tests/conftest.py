import pytest
from fastapi.testclient import TestClient
from main import app
from config.db import SessionLocal
from config.db import Base, engine

    
@pytest.fixture(scope="session")
def test_app():
    client = TestClient(app)
    yield client

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function",autouse=True)
def test_db_session(test_app):
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()