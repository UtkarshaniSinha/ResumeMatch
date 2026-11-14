from flask import flash, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFError

from app.extensions import db

# custom error pages so users never see error details / tracebacks


def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    # request bigger than MAX_CONTENT_LENGTH
    @app.errorhandler(413)
    def file_too_large(error):
        flash("The file is too large. The maximum size is 2 MB.", "error")
        return redirect(url_for("main.index"))

    @app.errorhandler(CSRFError)
    def csrf_failed(error):
        flash("Your form expired or was invalid. Please try again.", "error")
        # send login/register forms back to the same page, everything else to home
        if request.path in (url_for("auth.login"), url_for("auth.register")):
            return redirect(request.path)
        return redirect(url_for("main.index"))

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("500.html"), 500
