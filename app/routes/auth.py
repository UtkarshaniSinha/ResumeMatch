from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from app.extensions import db
from app.forms import DeleteAccountForm, LoginForm, RegisterForm
from app.models import SavedAnalysis, User

auth_bp = Blueprint("auth", __name__)


def get_current_user():
    # user_id is stored in the session after login
    # (flask signs the session cookie with SECRET_KEY so it can't be edited)
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return db.session.get(User, user_id)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if get_current_user() is None:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapper


def log_user_in(user):
    # keep the last result so the user can still save it after logging in
    last_result = session.get("last_result")

    # clear old session first (prevents session fixation)
    session.clear()
    session["user_id"] = user.id
    if last_result:
        session["last_result"] = last_result


def redirect_after_login():
    # if they analysed something before logging in, take them back to it
    if "last_result" in session:
        return redirect(url_for("main.results"))
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        if User.query.filter_by(username=username).first():
            flash("That username is already taken.", "error")
        else:
            user = User(username=username)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            log_user_in(user)
            flash("Account created. Welcome!", "success")
            return redirect_after_login()
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        user = User.query.filter_by(username=username).first()

        if user and user.is_locked():
            minutes = user.minutes_until_unlock()
            flash(f"Too many wrong passwords. Try again in {minutes} minute(s).", "error")
        elif user and user.check_password(form.password.data):
            user.record_successful_login()
            db.session.commit()
            log_user_in(user)
            flash("Logged in.", "success")
            return redirect_after_login()
        else:
            if user:
                user.record_failed_login()
                db.session.commit()
                if user.is_locked():
                    current_app.logger.warning("Account %r locked after too many wrong passwords", username)
            # goes to the server log, so brute force attempts can be seen there
            # (never log the password itself).
            # %r instead of %s: a username typed with a newline in it
            # can't add a fake extra line to the log
            current_app.logger.warning("Failed login for username %r", username)
            # same message for wrong username and wrong password,
            # otherwise someone can find out which usernames exist
            flash("Wrong username or password.", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("main.index"))


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = get_current_user()
    form = DeleteAccountForm()

    if form.validate_on_submit():
        if not user.check_password(form.password.data):
            flash("Wrong password. Your account was not deleted.", "error")
        else:
            # delete the user's saved analyses first, then the user
            SavedAnalysis.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
            session.clear()
            flash("Your account and all your saved analyses have been deleted.", "success")
            return redirect(url_for("main.index"))

    saved_count = SavedAnalysis.query.filter_by(user_id=user.id).count()
    return render_template("account.html", form=form, user=user, saved_count=saved_count)
