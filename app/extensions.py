from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# created here and connected to the app in create_app()
# (keeping them in a separate file avoids circular imports)
db = SQLAlchemy()
csrf = CSRFProtect()
