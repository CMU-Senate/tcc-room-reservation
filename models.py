import datetime
import functools
import operator

from setup import app, db, db_session

from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.orm import validates

admins = app.config['config']['DEFAULT']['ADMINS'].split(' ')

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

    def email(self, template='%s@andrew.cmu.edu'):
        return template % id

    def __repr__(self):
        return '<User: %s>' % self.id

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.String(500))
    reservable = db.Column(db.Boolean)
    reservations = db.relationship('Reservation', backref='room', lazy='dynamic')

    def __repr__(self):
        return '<Room: %s>' % self.name

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    cancelled = db.Column(db.Boolean, default=False)

    def duration(self):
        return self.end - self.start

    def __repr__(self):
        return '<Reservation: %s by %s from %s-%s>' % (self.room, self.user, self.start, self.end)

    @staticmethod
    def contiguous_before(reservations, start):
        reservation_before = reservations.filter(Reservation.end == start).first()
        if reservation_before:
            return [reservation_before] + Reservation.contiguous_before(reservations, reservation_before.start)
        return []

    @staticmethod
    def contiguous_after(reservations, end):
        reservation_after = reservations.filter(Reservation.start == end).first()
        if reservation_after:
            return [reservation_after] + Reservation.contiguous_after(reservations, reservation_after.end)
        return []

    @validates('user_id', 'room_id', 'start', 'end')
    def validates_times(self, key, value):
        if key == 'end':
            start, end = self.start, value
            now = datetime.datetime.now()
            duration = end - start

            week_start = start.date() - datetime.timedelta(days=start.weekday())
            week_end = week_start + datetime.timedelta(days=7)

            day_start = start.date()
            day_end = day_start + datetime.timedelta(days=1)

            admin = self.user_id in admins
            room = db_session.query(Room).filter_by(id=int(self.room_id)).first()
            config = functools.partial(app.config['config'].getint, 'SCHEDULING')
            user_reservations = room.reservations.filter(
                (Reservation.id != self.id) &
                (Reservation.cancelled == False) & # noqa: E712 (SQLAlchemy requires it)
                (Reservation.user_id == self.user_id)
            )

            contiguous_reservations = Reservation.contiguous_before(user_reservations, start) + Reservation.contiguous_after(user_reservations, end)
            contiguous_duration = sum(map(operator.methodcaller('duration'), contiguous_reservations), datetime.timedelta())

            week_reservations = user_reservations.filter((Reservation.start >= week_start) & (Reservation.start <= week_end)).all()
            week_reservation_duration = sum(map(operator.methodcaller('duration'), week_reservations), datetime.timedelta())

            day_reservations = user_reservations.filter((Reservation.start >= day_start) & (Reservation.start <= day_end)).all()
            day_reservation_duration = sum(map(operator.methodcaller('duration'), day_reservations), datetime.timedelta())

            assert start > now, \
                'Reservation must start in the future'
            assert (start - now) <= datetime.timedelta(days=config('MAX_DAYS_IN_FUTURE')), \
                'Reservation must start in the next %d days' % config('MAX_DAYS_IN_FUTURE')
            assert end > start, \
                'Reservation must end after it starts'
            assert admin or datetime.timedelta(minutes=config('MINIMUM_DURATION_MINUTES')) <= duration, \
                'Reservation must be at least %d minutes' % config('MINIMUM_DURATION_MINUTES')
            assert admin or duration <= datetime.timedelta(hours=config('MAX_CONTIGUOUS_DURATION_HOURS')), \
                'Reservation must not be longer than %d hours' % config('MAX_CONTIGUOUS_DURATION_HOURS')
            assert admin or duration + contiguous_duration <= datetime.timedelta(hours=config('MAX_CONTIGUOUS_DURATION_HOURS')), \
                'Reservations must not be longer than %d contiguous hours' % config('MAX_CONTIGUOUS_DURATION_HOURS')
            assert room.reservations.filter(Reservation.cancelled == False, Reservation.id != self.id).filter( # noqa: E712 (SQLAlchemy requires it)
                ((Reservation.start <= start) & (Reservation.end > start)) |
                ((Reservation.start >= start) & (Reservation.end <= end)) |
                ((Reservation.start < end) & (Reservation.end >= end))
            ).count() == 0, \
                'Reservation must not overlap with another'
            assert admin or duration + week_reservation_duration <= datetime.timedelta(hours=config('MAX_WEEK_HOURS')), \
                'Reservations must not exceed %d hours per week' % config('MAX_WEEK_HOURS')
            assert admin or duration + day_reservation_duration <= datetime.timedelta(hours=config('MAX_DAY_HOURS')), \
                'Reservations must not exceed %d hours per day' % config('MAX_DAY_HOURS')
        return value
