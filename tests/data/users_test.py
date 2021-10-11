import re
import uuid

from app.data.users import User
from app.data.users import UserGenerator


def _assert_user_defaults(user: User):
    assert user.enabled
    assert user.confirmed
    assert user.account_non_expired
    assert user.account_non_locked
    assert user.credentials_non_expired


def _assert_password_len(password: str):
    assert len(password) == 60


def test_user_generator_password():
    # hash result is 60 characters
    password = UserGenerator.generate_password(password_len=10)
    _assert_password_len(password)
    password = UserGenerator.generate_password(password_len=20)
    _assert_password_len(password)


def _assert_is_email(email: str):
    assert '@' in email
    parts = email.split('@')
    assert re.match('^[a-z0-9]+$', parts[0])
    assert re.match('^[a-z]+\\.(com|net|org|gov)$', parts[1])


def test_user_generator_email():
    email = UserGenerator.generate_email(min_len=20, max_len=25)
    _assert_is_email(email)


def test_user_generator_user():
    user = UserGenerator.generate_user(User.Role.ADMIN)

    assert isinstance(user.id, uuid.UUID)
    assert len(user.id.bytes) == len(uuid.uuid4().bytes)
    assert user.user_role == User.Role.ADMIN
    _assert_password_len(user.password)
    _assert_is_email(user.email)
    _assert_user_defaults(user)
