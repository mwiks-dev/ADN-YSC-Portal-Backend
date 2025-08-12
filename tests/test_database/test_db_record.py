import pytest

from models.user import User

def test_inserting_record(test_db_session):
    new_user = User(
        id=1,
        name="John Doe",
        email="johndoe@test.com",
        phonenumber="12345678910",
        password="test",
        role="parish_member"
        )
    test_db_session.add(new_user)
    test_db_session.commit()
    test_db_session.refresh(new_user)
    
    assert new_user is not None
    assert new_user.name == "John Doe"
    assert new_user.email == "johndoe@test.com"