from app.services.analyzer import analyze_resume
from app.services.resume_checks import (
    has_email,
    has_phone,
    has_heading,
    has_profile_link,
    run_resume_checks,
    EDUCATION_HEADINGS,
    PROJECT_HEADINGS,
)

GOOD_RESUME = """Priya Sharma
priya@example.com | +91 98765 43210
github.com/priya

Education
B.E. Computer Engineering

Projects
Face attendance app in Python and Flask
"""


def test_contact_details_found_and_missing():
    assert has_email("Contact: priya@example.com")
    assert not has_email("Contact: priya at example dot com")
    assert has_phone("Phone: +91 98765 43210")
    assert not has_phone("Phone: 12345")
    # year ranges should not count as a phone number
    assert not has_phone("B.E. 2023 - 2027 2019-2021\nHSC 2017 - 2019")
    assert has_profile_link("https://www.LinkedIn.com/in/priya")
    assert not has_profile_link("No links here")


def test_section_must_be_a_heading():
    assert has_heading("EDUCATION\nB.E. 2027", EDUCATION_HEADINGS)
    assert has_heading("Educational Qualifications\nB.E.", EDUCATION_HEADINGS)
    assert not has_heading("I value education a lot", EDUCATION_HEADINGS)
    assert has_heading("Academic Projects\nChat app", PROJECT_HEADINGS, allow_word_before=True)
    assert has_heading("PROJECTS:\nChat app", PROJECT_HEADINGS, allow_word_before=True)
    # a normal sentence starting with "project" is not a heading
    assert not has_heading("Managed project timelines", PROJECT_HEADINGS, allow_word_before=True)
    assert not has_heading("Delivered projects on time", PROJECT_HEADINGS, allow_word_before=True)


def test_all_checks_pass_for_good_resume():
    results = run_resume_checks(GOOD_RESUME)
    assert len(results) == 5
    assert all(check["passed"] for check in results)


def test_all_checks_fail_for_empty_resume():
    results = run_resume_checks("")
    assert not any(check["passed"] for check in results)


def test_analyze_resume_returns_everything():
    job = "We need a Python and Flask developer who knows Docker."
    result = analyze_resume(GOOD_RESUME, job)
    assert result["matched_skills"] == ["Flask", "Python"]
    assert result["missing_skills"] == ["Docker"]
    assert 0 < result["score"] <= 100
    assert len(result["checks"]) == 5
