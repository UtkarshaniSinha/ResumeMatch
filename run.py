import os

from app import create_app
from app.extensions import db

# gunicorn uses this "app" variable  ->  gunicorn run:app
app = create_app()

if __name__ == "__main__":
    # create sqlite tables when running locally
    with app.app_context():
        db.create_all()

    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
