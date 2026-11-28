import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.db import Base, get_db
from app.main import app
from app.seed.seed import seed_database
from app.models.models import User
from app.core.security import hash_password, create_access_token

# In-memory SQLite for high-speed local and CI unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    user = User(
        email="testuser@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user.id, "email": test_user.email, "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(db):
    user = User(
        email="seconduser@example.com",
        password_hash=hash_password("password123"),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def second_auth_headers(second_user):
    token = create_access_token({"sub": second_user.id, "email": second_user.email, "role": second_user.role})
    return {"Authorization": f"Bearer {token}"}
