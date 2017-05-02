from setup import db_session
from schemas import reservation_schema, reservations_schema
from models import User

import flask_login
from flask_login import logout_user
from flask import g, flash

def inject_user():
    try:
        return {'user': g.user if g.user.is_authenticated else None}
    except AttributeError:
        return {'user': None}

def global_user():
    g.user = flask_login.current_user

    if g.user and g.user.is_authenticated and g.user.banned:
        flash('You have been banned. Please contact us if you would like to appeal this decision.')
        logout_user()

    reservation_schema.context = {'user': g.user}
    reservations_schema.context = {'user': g.user}

def load_user(id):
    try:
        return db_session.query(User).get(id)
    except (TypeError, ValueError):
        pass
