from flask import Flask, url_for, request, abort, redirect, session, render_template, escape, flash, g
from flask_sqlalchemy import SQLAlchemy
import settings
import os
from flask import template_rendered
from contextlib import contextmanager

app = Flask(__name__)
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(100), unique=True, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.username


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


@app.route('/')
def indexView():
    if 'username' in session:
        print(session['username'])
        return 'Welcome %s !' % (escape(session['username']))
    return 'Hello!'


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profileView(username):
    return url_for("profile", username=username)


@app.route('/login', methods=['GET', 'POST'])
def loginView():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('indexView'))
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logoutView():
    if 'username' in session:
        if request.form.get('loginClick') == 'Logout':
            session.pop('username', None)
            return redirect(url_for('indexView'))
        else:
            return render_template('logout.html', username=session["username"])
    else:
        return redirect(url_for('indexView'))


@app.route('/add_user', methods=['GET'])
def add_user():
    username = request.args.get('username', None)
    phone = request.args.get('phone', None)
    if username is not None and phone is not None:
        user = User(username=username, phone=phone)
        get_db().session.add(user)
        get_db().session.commit()
    return "Ok!"


global_settings = GlobalSetting(settings)

app.config['SQLALCHEMY_DATABASE_URI'] = hasattr(
    global_settings, "SQLALCHEMY_DATABASE_URI")

db.init_app(app)


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


if __name__ == '__main__':
    # app.debug = True
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    with record_templates(app) as template_rendered_record:
        app.run(port=getattr(
            global_settings, "WEBPROT"))
