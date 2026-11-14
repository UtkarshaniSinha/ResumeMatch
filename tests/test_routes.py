import pytest

from app import create_app
from app.models import SavedAnalysis
from app.services.skill_finder import load_skills
from config import DEV_SECRET_KEY, ProductionConfig, TestConfig, get_database_url
from tests.conftest import logout, read_fixture, register, upload


def test_upload_redirects_to_results_page(client):
    # nothing analysed yet -> sent back to home
    assert client.get("/results").status_code == 302

    response = upload(client, read_fixture("sample_resume.pdf"))
    assert response.status_code == 302
    assert response.headers["Location"] == "/results"

    # refreshing the results page works and doesn't need the form again
    for _ in range(2):
        response = client.get("/results")
        assert b"Your results" in response.data
        assert b"Flask" in response.data


def test_sample_data_button(client):
    response = client.post("/sample", follow_redirects=True)
    assert b"Your results" in response.data
    assert b"Python" in response.data


def test_upload_fake_pdf_shows_friendly_error(client):
    response = upload(client, read_fixture("not_a_pdf.pdf"))
    assert response.status_code == 400
    assert b"not a real PDF" in response.data


def test_upload_over_size_limit_is_rejected(client):
    huge = b"%PDF-" + b"0" * (4 * 1024 * 1024)  # 4 MB
    response = upload(client, huge)
    assert response.status_code == 302
    assert b"too large" in client.get("/").data


def save_one_analysis(client, title="My test"):
    upload(client, read_fixture("sample_resume.pdf"))
    return client.post("/history/save", data={"title": title}, follow_redirects=True)


def test_history_needs_login(client):
    response = client.get("/history/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_save_and_list_analysis(client):
    # analyse first, then sign up - the result should still be there to save
    upload(client, read_fixture("sample_resume.pdf"))
    response = register(client)
    assert b"Your results" in response.data

    response = client.post("/history/save", data={"title": "My test"}, follow_redirects=True)
    assert b"Analysis saved" in response.data
    assert b"My test" in response.data


def test_user_can_delete_own_analysis(client):
    register(client)
    save_one_analysis(client)
    analysis = SavedAnalysis.query.first()

    client.post(f"/history/{analysis.id}/delete")
    assert SavedAnalysis.query.count() == 0


def test_save_limit_per_user(client, monkeypatch):
    monkeypatch.setattr("app.routes.history.MAX_SAVED_ANALYSES", 2)
    register(client)
    save_one_analysis(client)
    save_one_analysis(client)
    response = save_one_analysis(client)
    assert b"You can save up to 2 analyses" in response.data
    assert SavedAnalysis.query.count() == 2


def test_user_cannot_view_or_delete_someone_elses_analysis(client):
    # priya saves an analysis
    register(client, username="priya")
    save_one_analysis(client)
    analysis_id = SavedAnalysis.query.first().id
    logout(client)

    # rahul tries to open and delete it
    register(client, username="rahul")
    assert client.get(f"/history/{analysis_id}").status_code == 404
    assert client.post(f"/history/{analysis_id}/delete").status_code == 404
    assert SavedAnalysis.query.count() == 1


def test_custom_404_page_has_no_error_details(client):
    response = client.get("/this-page-does-not-exist")
    assert response.status_code == 404
    assert b"Page not found" in response.data
    assert b"Traceback" not in response.data


def test_form_without_csrf_token_is_rejected():
    class CsrfOnConfig(TestConfig):
        WTF_CSRF_ENABLED = True

    app = create_app(CsrfOnConfig)
    client = app.test_client()
    response = client.post("/login", data={"username": "a", "password": "b"})
    assert response.headers["Location"] == "/login"  # back to the same page
    assert b"form expired or was invalid" in client.get("/login").data


def test_production_settings():
    class BadProductionConfig(ProductionConfig):
        SECRET_KEY = DEV_SECRET_KEY

    with pytest.raises(RuntimeError):
        create_app(BadProductionConfig)

    class GoodProductionConfig(ProductionConfig):
        SECRET_KEY = "a-real-secret"
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    app = create_app(GoodProductionConfig)
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.debug is False
    response = app.test_client().get("/")
    assert "Strict-Transport-Security" in response.headers


def test_security_headers(client):
    response = client.get("/")
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]


def test_session_cookie_stays_small(client):
    # browsers drop cookies over ~4 KB. Worst case: job asks for every skill in our list
    skills = load_skills()
    job_text = " ".join(keywords[0] for keywords in skills.values())
    upload(client, read_fixture("sample_resume.pdf"), job_text=job_text)
    cookie = client.get_cookie("session")
    assert len(cookie.value) < 4000


def test_postgres_url_is_fixed_for_sqlalchemy(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://user:pw@host/db")
    assert get_database_url() == "postgresql://user:pw@host/db"
