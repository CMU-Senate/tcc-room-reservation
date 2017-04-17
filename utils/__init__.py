from setup import app, version
from .csrf import update_csrf_token

from flask import jsonify
from htmlmin.minify import html_minify
from webassets.filter import get_filter

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
    tracking_id = app.config['config'].get('DEFAULT', 'GOOGLE_ANALYTICS_TRACKING_ID')
    return {'google_analytics_tracking_id': tracking_id} if tracking_id else {}

def inject_recaptcha_key():
    recaptcha_key = app.config['config'].get('DEFAULT', 'RECAPTCHA_SITE_KEY')
    return {'recaptcha_site_key': recaptcha_key} if recaptcha_key else {}

def inject_version():
    return {'version': version}

def inject_filters():
    return {
        'babel': get_filter('babel', presets='babili,env', binary='node_modules/babel-cli/bin/babel.js'),
        'sass': get_filter('sass', as_output=True, style='compressed', binary='node_modules/node-sass/bin/node-sass')
    }
