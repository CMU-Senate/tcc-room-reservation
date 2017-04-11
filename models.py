from setup import db

from flask_login import UserMixin
from sqlalchemy.sql import func

admins = [
    'scherivi'
]

class User(db.Model, UserMixin):
    id = db.Column(db.String(8), primary_key=True) # Andrew ID
    username = db.Column(db.String(100)) # required for Social Flask
    admin = db.Column(db.Boolean)
    last_login = db.Column(db.DateTime, default=func.now())

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', kwargs.get('email').split('@')[0])
        self.username = self.id
        self.admin = kwargs.get('admin', self.id in admins)

    def __repr__(self):
        return 'User <%r>' % self.id
