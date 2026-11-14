from app.services.match_score import calculate_match_score, calculate_skill_score, combine_scores
from app.services.resume_checks import run_resume_checks
from app.services.skill_finder import compare_skills, find_skills, load_skills


def analyze_resume(resume_text, job_text, skills=None):
    # runs all the steps and returns one dict for the results page
    if skills is None:
        skills = load_skills()

    resume_skills = find_skills(resume_text, skills)
    job_skills = find_skills(job_text, skills)
    matched, missing = compare_skills(resume_skills, job_skills)

    skill_score = calculate_skill_score(matched, job_skills)
    text_score = calculate_match_score(resume_text, job_text)

    return {
        "score": combine_scores(skill_score, text_score),
        "skill_score": skill_score,
        "text_score": text_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "checks": run_resume_checks(resume_text),
    }
