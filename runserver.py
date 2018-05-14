from contextlib import contextmanager
from flask import template_rendered, Flask, g
from config import global_settings
from db import config_db
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
config_db(app)

from api import api_app
from web import web_app

configBluePrint(app)
with record_templates(app) as template_rendered_record:
    pass


if __name__ == '__main__':
    # app.debug = True
    app.run(port=getattr(
        global_settings, "WEBPROT"))
