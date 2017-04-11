#!/usr/bin/env python3

from config import app, login_manager, version, db_session
from models import User

from flask import render_template, g

import flask_login
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

@app.context_processor
def inject_version():
    return dict(version=version)

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

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
