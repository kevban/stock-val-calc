from flask_sqlalchemy import SQLAlchemy
from datetime import date

"""Models for app_name."""

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)