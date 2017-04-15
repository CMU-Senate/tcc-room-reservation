import secrets

from flask import request, session, abort

def update_csrf_token():
    csrf_token = secrets.token_hex(32)
    session['csrf_token'] = csrf_token
    return csrf_token

def check_csrf_token():
    if request.method == 'POST':
        correct_token = session.pop('csrf_token', None)
        received_token = request.form.get('csrfToken', None) or request.headers.get('X-CSRF-Token', None)
        if not correct_token or correct_token != received_token:
            abort(403)

def inject_csrf_token():
    return {'csrf_token': update_csrf_token()}
