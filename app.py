#!/usr/bin/env python3

import datetime

from setup import app, login_manager, version, db_session, manager
from models import User

import flask_login
from flask import render_template, g, request, session, redirect
from flask_login import logout_user
from htmlmin.minify import html_minify

@login_manager.user_loader
def load_user(id):
    try:
        return db_session.query(User).get(id)
    except (TypeError, ValueError):
        pass

@app.before_request
def global_user():
    g.user = flask_login.current_user

@app.after_request
def minify_html(response):
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            html_minify(response.get_data(as_text=True))
        )
    return response

@app.context_processor
def inject_anlytics_tracking_id():
    if 'GOOGLE_ANALYTICS_TRACKING_ID' in app.config:
        return dict(google_analytics_tracking_id=app.config['GOOGLE_ANALYTICS_TRACKING_ID'])
    else:
        return {}

@app.context_processor
def inject_version():
    return dict(version=version)

@app.context_processor
def inject_user():
    try:
        return {'user': g.user if g.user.is_authenticated else None}
    except AttributeError:
        return {'user': None}

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/')
def index():
    if request.args.get('logged_in', False):
        session['last_login'] = g.user.last_login
        g.user.last_login = datetime.datetime.now()
        db_session.commit()

    template = 'index.html'
    if g.user and g.user.is_authenticated:
        template = 'reservations.html'

    return render_template(template)

if __name__ == '__main__':
    manager.run()
