from setup import app, version
from .csrf import update_csrf_token

from flask import jsonify
from htmlmin.minify import html_minify

def success():
    return jsonify({
        'success': True,
        'csrf_token': update_csrf_token()
    })

def error(message):
    return jsonify({
        'success': False,
        'error': message,
        'csrf_token': update_csrf_token()
    })

def minify_html(response):
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            html_minify(response.get_data(as_text=True))
        )
    return response

def inject_anlytics_tracking_id():
    if 'GOOGLE_ANALYTICS_TRACKING_ID' in app.config:
        return dict(google_analytics_tracking_id=app.config['GOOGLE_ANALYTICS_TRACKING_ID'])
    else:
        return {}

def inject_version():
    return dict(version=version)
