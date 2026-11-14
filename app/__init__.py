from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.extensions import csrf, db
from app.services.resume_checks import CHECK_TIPS
from config import DEV_SECRET_KEY, choose_config


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        config_class = choose_config()
    app.config.from_object(config_class)

    # don't start in production with the default secret key
    if app.config["IS_PRODUCTION"] and app.config["SECRET_KEY"] == DEV_SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable must be set in production.")

    db.init_app(app)
    csrf.init_app(app)

    # on the server https is handled by the load balancer before the request
    # reaches flask. ProxyFix reads the X-Forwarded-Proto header so flask
    # knows the original request was https
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    from app.routes.auth import auth_bp, get_current_user
    from app.routes.errors import register_error_handlers
    from app.routes.history import history_bp
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(history_bp)
    register_error_handlers(app)

    # so every template can use {{ current_user }} and {{ check_tips }}
    @app.context_processor
    def inject_template_values():
        return {"current_user": get_current_user(), "check_tips": CHECK_TIPS}

    @app.after_request
    def add_security_headers(response):
        # page can't be shown inside an iframe on another site (clickjacking)
        response.headers["X-Frame-Options"] = "DENY"
        # browser must not guess the file type
        response.headers["X-Content-Type-Options"] = "nosniff"
        # only load scripts/styles/images from our own site, forms only submit to our site
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if app.config["IS_PRODUCTION"]:
            # tells the browser to always use https for this site (1 year)
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    # flask --app run create-tables
    @app.cli.command("create-tables")
    def create_tables():
        db.create_all()
        print("Tables created.")

    return app
