from flask_sqlalchemy import SQLAlchemy
from config import global_settings
db = SQLAlchemy()


def config_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = hasattr(
    global_settings, "SQLALCHEMY_DATABASE_URI")
    db.init_app(app)
    return db