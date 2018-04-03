from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
import settings


class GlobalSetting(object):
    def __init__(self, setting_module):
        for setting_key in dir(setting_module):
            setattr(self, setting_key, getattr(setting_module, setting_key))
        self.SETTINGS_MODULE = setting_module

    def __repr__(self):
        return '<%(cls)s "%(settings_module)s">' % {
            'cls': self.__class__.__name__,
            'settings_module': self.SETTINGS_MODULE,
        }


def get_db():
    db_connector = getattr(g, 'mysql_db', None)
    if db_connector is None:
        db_connector = g.mysql_db = db
    return db_connector


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db = SQLAlchemy()
global_settings = GlobalSetting(settings)
app.config['SQLALCHEMY_DATABASE_URI'] = hasattr(
    global_settings, "SQLALCHEMY_DATABASE_URI")
db.init_app(app)

from .handlers import web_app
