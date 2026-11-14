from app.extensions import db
from app.models.user import utc_now


# only the results are saved, not the resume file
class SavedAnalysis(db.Model):
    __tablename__ = "saved_analyses"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)

    score = db.Column(db.Float, nullable=False)
    skill_score = db.Column(db.Float, nullable=True)  # None if job has no skills from our list
    text_score = db.Column(db.Float, nullable=False)

    # lists of skills / checks stored as JSON (works in sqlite and postgres)
    matched_skills = db.Column(db.JSON, nullable=False)
    missing_skills = db.Column(db.JSON, nullable=False)
    checks = db.Column(db.JSON, nullable=False)

    job_snippet = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
