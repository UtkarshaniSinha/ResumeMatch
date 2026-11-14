from datetime import timedelta

from app.extensions import db
from app.models import SavedAnalysis, User
from app.models.user import utc_now
from tests.conftest import login, logout, read_fixture, register, upload


def test_register_stores_hashed_password(client):
    response = register(client)
    assert b"Account created" in response.data

    user = User.query.filter_by(username="priya").first()
    assert user.password_hash != "password123"
    assert user.check_password("password123")

    # same username with different case is not allowed
    logout(client)
    response = register(client, username="Priya")
    assert b"already taken" in response.data


def test_login_with_wrong_password_is_logged(client, caplog):
    register(client)
    logout(client)
    response = login(client, password="wrongpass1")
    assert b"Wrong username or password" in response.data
    assert "Failed login for username 'priya'" in caplog.text
    assert "wrongpass1" not in caplog.text  # password never goes in the log


def test_account_locks_after_5_wrong_passwords(client):
    register(client)
    logout(client)
    for _ in range(5):
        login(client, password="wrongpass1")

    # correct password should also fail while locked
    response = login(client)
    assert b"Too many wrong passwords" in response.data


def test_lock_ends_after_10_minutes(client):
    register(client)
    logout(client)
    user = User.query.filter_by(username="priya").first()
    user.locked_until = utc_now() - timedelta(minutes=1)  # lock already expired
    db.session.commit()

    response = login(client)
    assert b"Logged in" in response.data


def test_delete_account_needs_correct_password(client):
    register(client)
    upload(client, read_fixture("sample_resume.pdf"))
    client.post("/history/save", data={"title": "test"})

    response = client.post("/account", data={"password": "wrongpass1"}, follow_redirects=True)
    assert b"was not deleted" in response.data
    assert User.query.count() == 1

    response = client.post("/account", data={"password": "password123"}, follow_redirects=True)
    assert b"have been deleted" in response.data
    assert User.query.count() == 0
    assert SavedAnalysis.query.count() == 0  # their analyses are gone too
    assert client.get("/history/").status_code == 302  # logged out
