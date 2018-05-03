from api import api_app
from contextlib import contextmanager
from flask import template_rendered, Flask, g
from web import web_app
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


def configBluePrint(flask_app):
    flask_app.register_blueprint(api_app, url_prefix='/api/v1')
    flask_app.register_blueprint(web_app)
    print(app.url_map)


@contextmanager
def record_templates(app):
    recorded = []

    def record(sender, template, context, ** extra):
        print('received template rendered sign~')
        print("sender:%s \n template:%s \n" % (sender, template))
        recorded.append((template, sender))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
db = SQLAlchemy()
global_settings = GlobalSetting(settings)
app.config['SQLALCHEMY_DATABASE_URI'] = hasattr(
    global_settings, "SQLALCHEMY_DATABASE_URI")
db.init_app(app)
configBluePrint(app)
with record_templates(app) as template_rendered_record:
    pass


if __name__ == '__main__':
    # app.debug = True
    app.run(port=getattr(
        global_settings, "WEBPROT"))
