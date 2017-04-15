import datetime

from setup import db, db_session

from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

admins = [
    'scherivi'
]

class User(db.Model, UserMixin):
    id = db.Column(db.String(8), primary_key=True) # Andrew ID
    username = db.Column(db.String(100)) # required for Social Flask
    admin = db.Column(db.Boolean)
    last_login = db.Column(db.DateTime, default=func.now())
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        self.id = kwargs.get('id', kwargs.get('email').split('@')[0])
        self.username = self.id
        self.admin = kwargs.get('admin', self.id in admins)

    def __repr__(self):
        return 'User <%r>' % self.id

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.String(500))
    reservable = db.Column(db.Boolean)
    reservations = db.relationship('Reservation', backref='room', lazy='dynamic')

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    cancelled = db.Column(db.Boolean, default=False)

    @validates('room_id', 'start', 'end')
    def validates_times(self, key, value):
        if key == 'end':
            start, end = self.start, value
            now = datetime.datetime.now()
            duration = end - start
            admin = self.user_id in admins
            room = db_session.query(Room).filter_by(id=int(self.room_id)).first()

            assert start > now, 'Reservation must start in the future'
            assert (start - now) <= datetime.timedelta(days=10), 'Reservation must start in the next 10 days'
            assert end > start, 'Reservation must end after it starts'
            assert admin or datetime.timedelta(minutes=30) <= duration, 'Reservation must be at least 30 minutes'
            assert admin or duration <= datetime.timedelta(hours=3), 'Reservation must not be longer than 3 hours'
            assert room.reservations.filter(not Reservation.cancelled, Reservation.id != self.id).filter( # noqa: E712
                ((Reservation.start <= start) & (Reservation.end > start)) |
                ((Reservation.start >= start) & (Reservation.end <= end)) |
                ((Reservation.start < end) & (Reservation.end >= end))
            ).count() == 0, 'Reservation must not overlap with another'
        return value
