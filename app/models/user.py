from datetime import datetime, timedelta, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db

MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 10


def utc_now():
    # sqlite can't store timezone, so we keep everything in UTC without tzinfo
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    # "user" is a reserved word in postgres
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    failed_logins = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    def set_password(self, password):
        # only the hash is saved, never the real password
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # login lock: 5 wrong passwords -> locked for 10 minutes

    def is_locked(self):
        return self.locked_until is not None and self.locked_until > utc_now()

    def minutes_until_unlock(self):
        seconds_left = (self.locked_until - utc_now()).total_seconds()
        return max(1, round(seconds_left / 60))

    def record_failed_login(self):
        self.failed_logins += 1
        if self.failed_logins >= MAX_FAILED_LOGINS:
            self.locked_until = utc_now() + timedelta(minutes=LOCK_MINUTES)
            self.failed_logins = 0

    def record_successful_login(self):
        self.failed_logins = 0
        self.locked_until = None
