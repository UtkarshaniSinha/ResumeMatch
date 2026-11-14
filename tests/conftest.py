import io
import os

import pytest

from app import create_app
from app.extensions import db
from config import TestConfig

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

JOB_TEXT = (
    "We are hiring a Python Developer Intern to build web apps with Flask, "
    "write SQL for PostgreSQL, use Git and deploy with Docker on AWS."
)


# new app + empty in-memory database for every test
@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, username="priya", password="password123"):
    data = {"username": username, "password": password, "confirm": password}
    return client.post("/register", data=data, follow_redirects=True)


def login(client, username="priya", password="password123"):
    data = {"username": username, "password": password}
    return client.post("/login", data=data, follow_redirects=True)


def logout(client):
    return client.post("/logout", follow_redirects=True)


def upload(client, file_bytes, job_text=JOB_TEXT):
    data = {"resume": (io.BytesIO(file_bytes), "resume.pdf"), "job_description": job_text}
    return client.post("/analyze", data=data, content_type="multipart/form-data")


def read_fixture(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()
