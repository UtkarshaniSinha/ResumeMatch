from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(resume_text, job_text):
    # TF-IDF converts both texts into vectors (one number per word).
    # cosine similarity = angle between the two vectors
    #   1 -> same direction (very similar), 0 -> nothing in common
    # same idea as comparing face embeddings
    if not resume_text.strip() or not job_text.strip():
        return 0.0

    # stop_words removes common words like "the", "and", "is"
    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        vectors = vectorizer.fit_transform([resume_text, job_text])
    except ValueError:
        # this happens if the text has only stop words
        return 0.0

    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    # float() because sklearn gives a numpy number, which can't be saved in the session
    return round(float(similarity) * 100, 1)


def calculate_skill_score(matched_skills, job_skills):
    # % of job skills that are present in the resume
    if len(job_skills) == 0:
        return None
    return round(len(matched_skills) / len(job_skills) * 100, 1)


def combine_scores(skill_score, text_score):
    # tf-idf score alone was too low even for good resumes (around 10-15%),
    # so final score = average of skill score and text score
    if skill_score is None:
        return text_score
    return round((skill_score + text_score) / 2, 1)
