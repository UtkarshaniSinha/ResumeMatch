import json
import os
import re

# skills.json format ->  "JavaScript": ["javascript", "js"]
# key = name shown on the page, list = words we search for
SKILLS_FILE = os.path.join(os.path.dirname(__file__), "skills.json")


def load_skills(path=SKILLS_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def contains_keyword(text, keyword):
    # simple "in" check doesn't work: "java" is inside "javascript",
    # "excel" is inside "excellent". So the keyword must not have a
    # letter/number right before or after it.
    # re.escape is needed for skills like c++ and c#
    pattern = r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def find_skills(text, skills):
    text = text.lower()
    found = []
    for skill_name, keywords in skills.items():
        for keyword in keywords:
            if contains_keyword(text, keyword):
                found.append(skill_name)
                break
    return sorted(found)


def compare_skills(resume_skills, job_skills):
    matched = [skill for skill in job_skills if skill in resume_skills]
    missing = [skill for skill in job_skills if skill not in resume_skills]
    return matched, missing
