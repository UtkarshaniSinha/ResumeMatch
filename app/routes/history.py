from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.forms import SaveForm
from app.models import SavedAnalysis
from app.models.user import utc_now
from app.routes.auth import get_current_user, login_required

history_bp = Blueprint("history", __name__, url_prefix="/history")

# so one account can't fill up the free database
MAX_SAVED_ANALYSES = 50


def get_own_analysis_or_404(analysis_id):
    # filter by user_id too, so changing the id in the URL
    # can't open someone else's analysis (they just get 404)
    user = get_current_user()
    return SavedAnalysis.query.filter_by(id=analysis_id, user_id=user.id).first_or_404()


@history_bp.route("/")
@login_required
def list_analyses():
    user = get_current_user()
    analyses = (
        SavedAnalysis.query.filter_by(user_id=user.id)
        .order_by(SavedAnalysis.created_at.desc())
        .all()
    )
    return render_template("history.html", analyses=analyses)


@history_bp.route("/save", methods=["POST"])
@login_required
def save():
    result = session.get("last_result")
    form = SaveForm()
    if result is None or not form.validate_on_submit():
        flash("Nothing to save. Please analyse a resume first.", "error")
        return redirect(url_for("main.index"))

    user = get_current_user()
    if SavedAnalysis.query.filter_by(user_id=user.id).count() >= MAX_SAVED_ANALYSES:
        flash(f"You can save up to {MAX_SAVED_ANALYSES} analyses. Please delete some old ones first.", "error")
        return redirect(url_for("history.list_analyses"))

    title = (form.title.data or "").strip()
    if title == "":
        title = "Analysis on " + utc_now().strftime("%d %b %Y")

    analysis = SavedAnalysis(
        user_id=user.id,
        title=title,
        score=result["score"],
        skill_score=result["skill_score"],
        text_score=result["text_score"],
        matched_skills=result["matched_skills"],
        missing_skills=result["missing_skills"],
        checks=result["checks"],
        job_snippet=result["job_snippet"],
    )
    db.session.add(analysis)
    db.session.commit()
    session.pop("last_result")  # so it doesn't get saved twice

    flash("Analysis saved.", "success")
    return redirect(url_for("history.list_analyses"))


@history_bp.route("/<int:analysis_id>")
@login_required
def view(analysis_id):
    analysis = get_own_analysis_or_404(analysis_id)
    return render_template("analysis_detail.html", analysis=analysis)


@history_bp.route("/<int:analysis_id>/delete", methods=["POST"])
@login_required
def delete(analysis_id):
    analysis = get_own_analysis_or_404(analysis_id)
    db.session.delete(analysis)
    db.session.commit()
    flash("Analysis deleted.", "success")
    return redirect(url_for("history.list_analyses"))
