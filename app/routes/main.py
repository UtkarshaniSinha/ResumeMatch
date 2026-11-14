import os

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from app.forms import AnalyzeForm, SaveForm
from app.services.analyzer import analyze_resume
from app.services.pdf_reader import PDFError, extract_text_from_pdf

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", form=AnalyzeForm())


@main_bp.route("/analyze", methods=["POST"])
def analyze():
    form = AnalyzeForm()
    if not form.validate_on_submit():
        return render_template("index.html", form=form), 400

    # read file into memory only, never saved
    file_bytes = form.resume.data.read()
    try:
        resume_text = extract_text_from_pdf(file_bytes)
    except PDFError as error:
        flash(str(error), "error")
        return render_template("index.html", form=form), 400

    return save_result_and_redirect(resume_text, form.job_description.data)


@main_bp.route("/sample", methods=["POST"])
def sample():
    # demo button: runs the analysis on a sample resume and job description
    sample_folder = os.path.join(current_app.static_folder, "sample")
    with open(os.path.join(sample_folder, "sample_resume.pdf"), "rb") as f:
        resume_text = extract_text_from_pdf(f.read())
    with open(os.path.join(sample_folder, "sample_job.txt"), encoding="utf-8") as f:
        job_text = f.read()

    return save_result_and_redirect(resume_text, job_text)


def save_result_and_redirect(resume_text, job_text):
    result = analyze_resume(resume_text, job_text)
    result["job_snippet"] = job_text[:150]

    # result is kept in the session, then we redirect to /results.
    # (Post/Redirect/Get - so refreshing the results page doesn't
    # submit the form again)
    session["last_result"] = result
    return redirect(url_for("main.results"))


@main_bp.route("/results")
def results():
    result = session.get("last_result")
    if result is None:
        flash("Please analyse a resume first.", "error")
        return redirect(url_for("main.index"))
    return render_template("results.html", result=result, save_form=SaveForm())
