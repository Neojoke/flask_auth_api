from .models import User
from flask import request, session, escape, redirect, url_for, render_template, Blueprint
from flask.views import View

web_app = Blueprint("web_app", __name__)
from db import db

@web_app.route('/')
def indexView():
    if 'username' in session:
        print(session['username'])
        return 'Welcome %s !' % (escape(session['username']))
    return 'Hello'


@web_app.route('/test')
def testView():
    return "test"


@web_app.route('/login', methods=['GET', 'POST'])
def loginView():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('indexView'))
    return render_template('login.html')


class ShowProfileView(View):
    methods = ['GET', 'POST']

    def dispatch_request(self, username):
        if request.method == 'POST':
            return "Forbidden POST"
        else:
            return "Profile:\n%s" % (username)


@web_app.route('/logout', methods=['GET', 'POST'])
def logoutView():
    if 'username' in session:
        if request.form.get('loginClick') == 'Logout':
            session.pop('username', None)
            return redirect(url_for('indexView'))
        else:
            return render_template('logout.html', username=session["username"])
    else:
        return redirect(url_for('indexView'))


@web_app.route('/add_user', methods=['GET'])
def add_user():
    username = request.args.get('username', None)
    phone = request.args.get('phone', None)
    if username is not None and phone is not None:
        user = User(username=username, phone=phone)
        db.session.add(user)
        db.session.commit()
    return "Ok!"


web_app.add_url_rule('/profile/<username>',
                     view_func=ShowProfileView.as_view("show_profile"))