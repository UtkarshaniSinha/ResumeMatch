# ResumeMatch

ResumeMatch checks how well a resume matches a job description. You upload your resume as a PDF, paste the job description, and it shows a match score, which skills you have, which ones are missing, and a few basic checks on the resume.

## Why I built this

During placement season I was changing my resume for almost every company, and I never knew if it actually matched what the job post was asking for. Most online "ATS checkers" ask you to sign up or pay before showing anything useful. So I decided to build a simple one myself.

I also wanted a project where I could learn the things my earlier projects didn't cover properly - login and password hashing, file upload security, writing tests, and putting an app on the cloud with a real database.

## Features

- Upload resume (PDF) + paste job description
- Match score from 0 to 100%
- Matched skills and missing skills (from a list of about 100 tech skills)
- 5 resume checks: email, phone number, GitHub/LinkedIn link, Education section, Projects section
- Sign up / log in to save results, see them later and delete them (up to 50 per user)
- Delete your account and all your data from the Account page
- Resume file is never saved, it is only read in memory
- "Try with sample data" button, so anyone can test it without uploading their own resume


## How it works

```
 Browser
    |  upload PDF + job description
    v
 Flask app
    |-- pdf_reader.py      checks it's a real PDF under 2 MB, extracts the text
    |-- skill_finder.py    finds skills (from skills.json) in both texts
    |-- match_score.py     TF-IDF + cosine similarity, skill score
    |-- resume_checks.py   email / phone / links / sections
    v
 Results page ---- save (if logged in) ----> database
```

### How the score is calculated

The final score is the average of two scores:

| Score | Meaning | Example |
|---|---|---|
| Skill score | how many of the job's skills are in the resume | 5 out of 9 = 55.6% |
| Text score | TF-IDF + cosine similarity between the two texts | 12.3% |
| Final | average of both | (55.6 + 12.3) / 2 = 34.0% |

At first I only used the TF-IDF score, but it was coming very low (around 10-15%) even for resumes that matched well, because a resume and a job post are written very differently. Adding the skill score made the result much more sensible.

**Cosine similarity:** TF-IDF turns each text into a vector (one number for every word). Cosine similarity checks the angle between the two vectors - if they point in the same direction the value is 1, if they have nothing in common it's 0. I had used the same thing before for comparing face embeddings in my face attendance project, so here I just used it on text instead of faces.

## Tech stack

| What | Used |
|---|---|
| Backend | Python 3.12, Flask |
| Frontend | Jinja templates, HTML, CSS (no JavaScript) |
| Database | SQLite (local), PostgreSQL (cloud) using Flask-SQLAlchemy |
| Forms + CSRF | Flask-WTF |
| PDF text | pdfplumber |
| Matching | scikit-learn |
| Server | gunicorn |
| Testing | pytest |

## Folder structure

```
resumematch/
|-- app/
|   |-- __init__.py      create_app()
|   |-- extensions.py    db and csrf objects
|   |-- forms.py         all forms
|   |-- models/          User, SavedAnalysis tables
|   |-- routes/          main, auth, history, error pages
|   |-- services/        resume analysis code + skills.json
|   |-- templates/       html pages
|   `-- static/          style.css, sample resume + job description
|-- tests/               pytest tests + test pdfs
|-- config.py
|-- run.py
|-- Procfile
|-- requirements.txt
`-- .env.example
```

## Run locally (Windows)

You need Python 3.12 installed.

```
git clone https://github.com/UtkarshaniSinha/resumematch.git
cd resumematch
py -3.12 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Put a random value for `SECRET_KEY` in the `.env` file. You can generate one with:

```
python -c "import secrets; print(secrets.token_hex(32))"
```

Then run:

```
python run.py
```

and open http://127.0.0.1:5000. The SQLite database gets created automatically inside the `instance` folder.

## Tests

```
python -m pytest -v
```

There are 40 tests. They cover PDF validation, skill matching, the scores, resume checks, register/login, the login lock and login logging, saving and deleting, the save limit, deleting an account, checking that one user can't open another user's data, CSRF, the upload size limit, security headers, session cookie size, error pages and the production settings.

## Security

| What I did | What it protects against |
|---|---|
| Passwords hashed using werkzeug | If the database leaks, real passwords are still safe |
| Login required for saved analyses | Others can't see or change saved data |
| Every query also checks the logged-in user's id (others get 404) | Changing the id in the URL to open someone else's data (IDOR) |
| CSRF token on all forms, logout and delete are POST forms | Other websites submitting forms using your login (CSRF) |
| PDF checked by its content (`%PDF-` at the start), not just the name | Uploading other files renamed as .pdf |
| 2 MB file limit, 3 MB request limit | Very large uploads slowing down the server |
| Empty, broken and scanned PDFs give a proper message | App crashing on bad files |
| Uploaded file only read in memory, never saved | Personal data lying around on the server |
| `SECRET_KEY` and `DATABASE_URL` from environment variables, `.env` in `.gitignore` | Secrets getting pushed to GitHub |
| App won't start in production without a real secret key | Fake session cookies made with a known key |
| Cookies are HttpOnly, SameSite=Lax, and Secure in production | Cookie stealing through JavaScript, cross-site requests, cookie sent over http |
| Session is cleared on login and logout | Session fixation |
| Same error message for wrong username and wrong password | Finding out which usernames exist |
| 5 wrong passwords = account locked for 10 minutes (saved in database) | Brute force password guessing |
| Failed logins and lockouts written to the server log (never the password) | Attacks going unnoticed - they can be seen in the server logs |
| Password needed again to delete the account | Someone deleting your account from a laptop you left logged in |
| Max 50 saved analyses per user | One account filling up the database |
| Debug off in production, custom 404 and 500 pages | Error pages showing code and file paths |
| `X-Frame-Options: DENY` and `frame-ancestors 'none'` | Clickjacking (my site loaded in a hidden frame on another site) |
| `Content-Security-Policy: default-src 'self'` | Loading scripts or styles from other websites, extra protection against XSS |
| `X-Content-Type-Options: nosniff` | Browser treating a file as a different type than it really is |
| `Strict-Transport-Security` in production | Browser ever opening the site over plain http |
| Jinja escapes all output | XSS |
| SQLAlchemy instead of writing SQL strings | SQL injection |

## Deployment

The app is made to run on AWS with a PostgreSQL database.

```
 Browser --https--> AWS (Flask + gunicorn) ---> PostgreSQL
```

What is needed on the server:

1. Install the packages from `requirements.txt`
2. Set these environment variables:
   - `SECRET_KEY` - a long random string
   - `DATABASE_URL` - the PostgreSQL connection string
   - `APP_ENV=production`
3. Create the tables once:
   ```
   flask --app run create-tables
   ```
4. Start the app with gunicorn (this is also in the `Procfile`):
   ```
   gunicorn run:app
   ```

HTTPS is handled by AWS in front of the app. `ProxyFix` in `app/__init__.py` makes Flask understand that the original request was https, so the secure cookie works properly.

## Limitations

- This is basically keyword matching with a fixed skill list. Real ATS software works differently in every company, so the score is only a rough guide.
- It doesn't understand synonyms or context. For example "react" used as a normal verb will still count as React.
- Scanned PDFs (images) can't be read because there is no OCR.
- The phone number check is simple. It ignores year ranges like 2023 - 2027, but it doesn't verify that the number is real.
- The login lock only works for usernames that exist.
- A section heading has to be on its own line. A heading with an extra word after it, like "Education Details", is not detected.

## What I learned

- Structuring a Flask app with blueprints and an app factory
- How TF-IDF and cosine similarity work on text
- How password hashing, sessions, cookies and CSRF actually work
- Why you should check a file's content and not trust its name
- Writing tests with pytest, including tests for security
- Post/Redirect/Get, so refreshing a page after a form doesn't submit it again
- Keeping secrets out of the code using environment variables

## Future improvements

- Let users add their own skills and synonyms (like "ML" = "Machine Learning")
- OCR for scanned resumes
- Suggestions for where to add missing skills in the resume
- Download the result as a PDF
