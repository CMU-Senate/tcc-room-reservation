import datetime

from setup import db, db_session, config

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

    @validates('user_id', 'room_id', 'start', 'end')
    def validates_times(self, key, value):
        if key == 'end':
            start, end = self.start, value
            now = datetime.datetime.now()
            duration = end - start

            admin = self.user_id in admins
            room = db_session.query(Room).filter_by(id=int(self.room_id)).first()
            user_reservations = room.reservation.filter(cancelled=False, user_id=self.user_id)
            config = config['SCHEDULING']

            assert start > now, \
                'Reservation must start in the future'
            assert (start - now) <= datetime.timedelta(days=config['MAX_DAYS_IN_FUTURE']), \
                'Reservation must start in the next %d days' % config['MAX_DAYS_IN_FUTURE']
            assert end > start, \
                'Reservation must end after it starts'
            assert admin or datetime.timedelta(minutes=config['MINIMUM_DURATION_MINUTES']) <= duration, \
                'Reservation must be at least %d minutes' % config['MINIMUM_DURATION_MINUTES']
            assert admin or duration <= datetime.timedelta(hours=config['MAX_CONTIGUOUS_DURATION_HOURS']), \
                'Reservation must not be longer than %d hours' % config['MAX_CONTIGUOUS_DURATION_HOURS']
            # TODO: this condition should take into account contiguous reservations
            # TODO: this condition isn't actually stopping overlaps
            assert room.reservations.filter(not Reservation.cancelled, Reservation.id != self.id).filter( # noqa: E712
                ((Reservation.start <= start) & (Reservation.end > start)) |
                ((Reservation.start >= start) & (Reservation.end <= end)) |
                ((Reservation.start < end) & (Reservation.end >= end))
            ).count() == 0, \
                'Reservation must not overlap with another'
            # TODO: maximum per week
        return value
