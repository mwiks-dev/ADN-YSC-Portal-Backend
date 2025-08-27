from models.parish import Parish
from models.deanery import Deanery
from models.user import User
from services.parish_service import (
    get_parishes,
    get_parish_by_id,
    get_parishes_by_deanery,
    get_all_users_of_parish,
    get_parish_by_name,
    create_parish,
    update_parish,
    delete_parish
)
import pytest

def test_create_parish(test_db_session):
    deanery = Deanery(name="Central")
    parish = create_parish(test_db_session, name="St. Peter", deanery=deanery)
    assert parish is not None
    assert parish.name == "St. Peter"
    assert parish.deanery.name == "Central"
    db_parish = test_db_session.query(type(parish)).filter_by(name="St. Peter").first()
    assert db_parish is not None

def test_get_parish_by_id(test_db_session):
    deanery = Deanery(name="North")
    parish = create_parish(test_db_session, name="St. Paul", deanery=deanery)
    fetched = get_parish_by_id(test_db_session, parish.id)
    assert fetched is not None
    assert fetched.name == "St. Paul"

def test_get_parish_by_name(test_db_session):
    deanery = Deanery(name="South")
    parish = create_parish(test_db_session, name="St. Mary", deanery=deanery)
    fetched = get_parish_by_name(test_db_session, "St. Mary")
    assert fetched is not None
    assert fetched.deanery.name == "South"

def test_get_parishes(test_db_session):
    deanery_one = Deanery(name="East")
    deanery_two = Deanery(name="West")
    create_parish(test_db_session, name="St. Mark", deanery=deanery_one)
    create_parish(test_db_session, name="St. Luke", deanery=deanery_two)
    parishes = get_parishes(test_db_session)
    assert len(parishes) >= 2

def test_get_parishes_by_deanery(test_db_session):
    deanery = Deanery(name="North West")
    create_parish(test_db_session, name="St. Andrew", deanery=deanery)
    create_parish(test_db_session, name="St. James", deanery=deanery)
    parishes = get_parishes_by_deanery(test_db_session, deanery=deanery).all()
    assert len(parishes) >= 2
    for parish in parishes:
        assert parish.deanery.name == "North West"

def test_update_parish(test_db_session):
    deanery_old = Deanery(name="Old Deanery")
    deanery_new = Deanery(name="New Deanery")
    parish = create_parish(test_db_session, name="Old Parish", deanery=deanery_old)
    updated = update_parish(test_db_session, parish.id, name="New Parish", deanery=deanery_new)
    assert updated.name == "New Parish"
    assert updated.deanery.name == "New Deanery"

def test_delete_parish(test_db_session):
    del_deanery = Deanery(name="Deleted deanery")
    parish = create_parish(test_db_session, name="Delete Parish", deanery=del_deanery)
    deleted = delete_parish(test_db_session, parish.id)
    assert deleted is not None
    assert test_db_session.query(Parish).filter_by(id=parish.id).first() is None

def test_get_all_users_of_parish(test_db_session):
    deanery = Deanery(name="User Deanery")
    parish = create_parish(test_db_session, name="User Parish", deanery=deanery)
    user1 = User(name="User1", email="user1@parish.com", phonenumber="1111111111", password="pass1", role="parish_member", parish_id=parish.id)
    user2 = User(name="User2", email="user2@parish.com", phonenumber="2222222222", password="pass2", role="parish_member", parish_id=parish.id)
    test_db_session.add(user1)
    test_db_session.add(user2)
    test_db_session.commit()
    users = get_all_users_of_parish(test_db_session, parish.id)
    assert len(users) == 2
    emails = [u.email for u in users]
    assert "user1@parish.com" in emails
    assert "user2@parish.com" in emails
