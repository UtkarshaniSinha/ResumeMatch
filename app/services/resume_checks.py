import re

EMAIL_PATTERN = r"[\w.+-]+@[\w-]+\.[\w.]+"

# starts and ends with a digit, spaces/dashes/brackets allowed in between
# (no newlines, so numbers on different lines don't join together)
# eg. +91 98765 43210, (020) 2345-6789
PHONE_PATTERN = r"\+?\d[\d ()-]{8,}\d"

# headings people actually use in resumes
EDUCATION_HEADINGS = ["education", "educational qualifications?", "academic details", "qualifications?"]
# one optional word before, like "Academic Projects" or "Personal Projects"
PROJECT_HEADINGS = ["projects?", "project work"]

# tips shown when a check fails
CHECK_TIPS = {
    "Email address": "Add a professional email so recruiters can contact you.",
    "Phone number": "Add a phone number with country code, e.g. +91.",
    "GitHub or LinkedIn link": "Add your GitHub or LinkedIn URL so recruiters can see your work.",
    "Education section": "Add an 'Education' heading with your degree and college.",
    "Projects section": "Add a 'Projects' heading. It matters a lot for freshers.",
}


def has_email(text):
    return re.search(EMAIL_PATTERN, text) is not None


def is_year_range(number_text):
    # "2023 - 2027" or "2019-2021 2021-2023" are years, not phone numbers
    groups = re.findall(r"\d+", number_text)
    return all(len(g) == 4 and g.startswith(("19", "20")) for g in groups)


def has_phone(text):
    for match in re.findall(PHONE_PATTERN, text):
        digits = [ch for ch in match if ch.isdigit()]
        if 10 <= len(digits) <= 13 and not is_year_range(match):
            return True
    return False


def has_profile_link(text):
    text = text.lower()
    return "github.com" in text or "linkedin.com" in text


def has_heading(text, headings, allow_word_before=False):
    # heading must be the whole line, otherwise "I value education" or a
    # bullet like "Managed project timelines" would also count.
    # [ \t] instead of \s so the match never jumps to the next line,
    # and symbols like ":" or "-" are allowed after the heading
    start = r"^[ \t]*"
    if allow_word_before:
        start += r"(\w+[ \t]+)?"
    end = r"[^\w\n]*$"
    pattern = start + "(" + "|".join(headings) + ")" + end
    return re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is not None


def run_resume_checks(text):
    # only name + passed is stored, tips come from CHECK_TIPS
    # (keeps the session cookie small)
    return [
        {"name": "Email address", "passed": has_email(text)},
        {"name": "Phone number", "passed": has_phone(text)},
        {"name": "GitHub or LinkedIn link", "passed": has_profile_link(text)},
        {"name": "Education section", "passed": has_heading(text, EDUCATION_HEADINGS)},
        {"name": "Projects section", "passed": has_heading(text, PROJECT_HEADINGS, allow_word_before=True)},
    ]
