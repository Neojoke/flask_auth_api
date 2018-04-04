from api import api_app
from contextlib import contextmanager
from flask import template_rendered
from web import app, web_app, global_settings


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


def configBluePrint(flask_app):
    flask_app.register_blueprint(api_app, url_prefix='/api/v1')
    flask_app.register_blueprint(web_app)
    print(app.url_map)


if __name__ == '__main__':
    with record_templates(app) as template_rendered_record:
        # app.debug = True
        configBluePrint(app)
        app.run(port=getattr(
            global_settings, "WEBPROT"))
