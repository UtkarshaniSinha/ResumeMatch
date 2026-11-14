from app.services.skill_finder import compare_skills, contains_keyword, find_skills, load_skills

# small list just for these tests
SMALL_SKILLS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "C++": ["c++", "cpp"],
    "Excel": ["excel"],
}


def test_skills_file_loads_and_has_about_100_skills():
    skills = load_skills()
    assert 90 <= len(skills) <= 120
    # common short forms used in Indian job posts
    assert find_skills("OOPS, DSA and ML", skills) == ["Data Structures", "Machine Learning", "OOP"]


def test_finds_skill_ignoring_case_and_by_alias():
    assert find_skills("I love PYTHON", SMALL_SKILLS) == ["Python"]
    assert find_skills("Built frontend in JS", SMALL_SKILLS) == ["JavaScript"]
    assert contains_keyword("skills: c++, python", "c++")


def test_java_is_not_found_inside_javascript():
    assert find_skills("Worked with JavaScript", SMALL_SKILLS) == ["JavaScript"]


def test_excel_is_not_found_inside_excellent():
    assert find_skills("Excellent team player", SMALL_SKILLS) == []


def test_compare_skills_splits_matched_and_missing():
    matched, missing = compare_skills(["Python", "C++"], ["Python", "Java"])
    assert matched == ["Python"]
    assert missing == ["Java"]
