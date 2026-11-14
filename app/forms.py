from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import PasswordField, StringField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Optional, Regexp

# FlaskForm automatically adds the csrf token (form.hidden_tag() in templates)


class AnalyzeForm(FlaskForm):
    resume = FileField(
        "Your resume (PDF, max 2 MB)",
        validators=[
            FileRequired("Please choose a PDF file."),
            # this only checks the file name, real check is in pdf_reader.py
            FileAllowed(["pdf"], "Only PDF files are allowed."),
        ],
    )
    job_description = TextAreaField(
        "Job description",
        validators=[
            DataRequired("Please paste the job description."),
            Length(min=50, max=10000, message="Job description must be 50 to 10,000 characters."),
        ],
    )


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30),
            Regexp(r"^[A-Za-z0-9_]+$", message="Use only letters, numbers and underscores."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords do not match.")],
    )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class SaveForm(FlaskForm):
    title = StringField("Name this analysis", validators=[Optional(), Length(max=100)])


class DeleteAccountForm(FlaskForm):
    # asking for the password again so nobody can delete the account
    # just by using a logged-in laptop
    password = PasswordField("Enter your password to confirm", validators=[DataRequired()])
