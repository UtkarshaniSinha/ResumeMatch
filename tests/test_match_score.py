from app.services.match_score import calculate_match_score, calculate_skill_score, combine_scores


def test_identical_texts_score_100():
    text = "Python developer with Flask and SQL experience"
    score = calculate_match_score(text, text)
    assert score == 100.0
    assert type(score) is float  # not numpy float


def test_completely_different_texts_score_0():
    assert calculate_match_score("python flask sql", "painting music dance") == 0.0


def test_better_resume_gets_higher_score():
    job = "Python Flask developer, SQL, REST APIs"
    good_resume = "Python Flask developer who built REST APIs with SQL"
    weak_resume = "Graphic designer skilled in Photoshop and Python"
    assert calculate_match_score(good_resume, job) > calculate_match_score(weak_resume, job)


def test_empty_or_stop_words_only_scores_0():
    assert calculate_match_score("", "Python developer") == 0.0
    assert calculate_match_score("Python developer", "   ") == 0.0
    assert calculate_match_score("the and is", "a an the") == 0.0


def test_skill_score_and_combined_score():
    assert calculate_skill_score(["Python"], ["Python", "Java"]) == 50.0
    assert calculate_skill_score([], []) is None
    assert combine_scores(50.0, 12.0) == 31.0
    assert combine_scores(None, 12.0) == 12.0
