import pytest
from models.user import User
from models.parish import Parish
from models.deanery import Deanery
from models.outstation import Outstation
from services.user_service import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_users,
    update_user,
    delete_user,
    authenticate_user,
    reset_password
)

def test_create_user(test_db_session):
    user = create_user(
        test_db_session,
        name="Jane Martin",
        email="janemartin@test.com",
        phonenumber="0987654321",
        password="securepassword"
    )
    assert user is not None
    assert user.name == "Jane Martin"
    assert user.email == "janemartin@test.com"
    assert user.role == "parish_member"
    db_user = test_db_session.query(User).filter_by(email="janemartin@test.com").first()
    assert db_user is not None

def test_get_user_by_id(test_db_session):
    user = create_user(
        test_db_session,
        name="John Smith",
        email="johnsmith@test.com",
        phonenumber="1234567890",
        password="password123",
        role="parish_member"
    )
    fetched = get_user_by_id(test_db_session, user.id)
    assert fetched is not None
    assert fetched.email == "johnsmith@test.com"

def test_get_user_by_email(test_db_session):
    user = create_user(
        test_db_session,
        name="Alice",
        email="alice@test.com",
        phonenumber="5555555555",
        password="alicepass",
        role="parish_member"
    )
    fetched = get_user_by_email(test_db_session, "alice@test.com")
    assert fetched is not None
    assert fetched.name == "Alice"

def test_get_users(test_db_session):
    create_user(test_db_session, "User1", "user1@test.com", "1111111111", "pass1")
    create_user(test_db_session, "User2", "user2@test.com", "2222222222", "pass2")
    users = get_users(test_db_session)
    assert len(users) >= 2

def test_update_user(test_db_session):
    parish = Parish(name="St Dominic")
    user = create_user(test_db_session, "Old Name", "old@test.com", "3333333333", "oldpass")
    updated = update_user(
        test_db_session,
        id=user.id,
        name="New Name",
        email="new@test.com",
        phonenumber="4444444444",
        password="newpass",
        parish=parish
    )
    assert updated.name == "New Name"
    assert updated.email == "new@test.com"
    assert updated.phonenumber == "4444444444"
    assert updated.parish.name == "St Dominic"

def test_delete_user(test_db_session):
    user = create_user(test_db_session, "Delete Me", "deleteme@test.com", "5555555555", "deletepass")
    deleted = delete_user(test_db_session, user.id)
    assert deleted is not None
    assert test_db_session.query(User).filter_by(id=user.id).first() is None

def test_authenticate_user(test_db_session):
    password = "authpass"
    user = create_user(test_db_session, "Auth User", "auth@test.com", "6666666666", password)
    authenticated = authenticate_user(test_db_session, "auth@test.com", password)
    assert authenticated is not None
    assert authenticated.email == "auth@test.com"
    assert authenticate_user(test_db_session, "auth@test.com", "wrongpass") is None
    assert authenticate_user(test_db_session, "nouser@test.com", "authpass") is None

def test_reset_password(test_db_session):
    user = create_user(test_db_session, "Reset User", "reset@test.com", "7777777777", "oldpass")
    reset_user = reset_password(test_db_session, "reset@test.com", "oldpass", "newpass")
    assert reset_user is not None
    assert authenticate_user(test_db_session, "reset@test.com", "newpass") is not None
    assert authenticate_user(test_db_session, "reset@test.com", "oldpass") is None
