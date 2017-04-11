#!/usr/bin/env python3

import datetime

from setup import app, login_manager, version, db_session, manager
from models import User, Room, Reservation
from schemas import reservation_schema, reservations_schema

import flask_login
from flask import render_template, g, request, session, redirect, jsonify, abort
from flask_login import logout_user, login_required
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
    reservation_schema.context = {'user': g.user}
    reservations_schema.context = {'user': g.user}

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

@app.route('/reservations/<int:room>')
@login_required
def get_reservations(room):
    room = Room.query.filter_by(id=room).first()
    if room:
        reservations = room.reservations.filter(Reservation.cancelled.in_([True, False] if g.user.admin else [False]))
        return reservations_schema.jsonify(reservations)
    else:
        return abort(404)

@app.route('/reservation/<int:reservation>')
@login_required
def get_reservation(reservation):
    reservation = Reservation.query.filter(id == reservation).first()
    if reservation:
        return reservation_schema.jsonify(reservation)
    else:
        return abort(404)

@app.route('/reservation/add', methods=['POST'])
@login_required
def add_reservation():
    start, end = request.form.get('start', None), request.form.get('end', None)
    room = request.form.get('room', None)
    if start and end and room:
        room = Room.query.filter_by(id=int(room)).first()
        if not room:
            return abort(400)

        start, end = datetime.datetime.utcfromtimestamp(int(start)), datetime.datetime.utcfromtimestamp(int(end))

        # TODO: Abstract validation to make edit_reservation easier
        starts_in_future = start > datetime.datetime.now()
        starts_in_near_future = starts_in_future and ((start - datetime.datetime.now()) <= datetime.timedelta(days=10))
        ends_after_start = end > start
        valid_duration = datetime.timedelta(minutes=30) <= (end - start) < datetime.timedelta(hours=2)
        overlaps = room.reservations.filter_by(cancelled=False).filter(
            ((Reservation.start <= start) & (Reservation.end > start)) |
            ((Reservation.start >= start) & (Reservation.end <= end)) |
            ((Reservation.start < end) & (Reservation.end >= end))
        ).count()
        if starts_in_near_future and ends_after_start and (valid_duration or g.user.admin) and overlaps == 0:
            db_session.add(Reservation(
                user_id=g.user.id,
                room_id=room.id,
                start=start,
                end=end
            ))
            db_session.commit()
            return jsonify({'success': True})
        else:
            return abort(400)
    else:
        return abort(400)

@app.route('/reservation/add', methods=['POST'])
@login_required
def edit_reservation():
    ... # TODO: Write this

@app.route('/reservation/<int:reservation>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation):
    reservation = Reservation.objects.filter_by(id=reservation)
    if reservation and (reservation.user_id == g.user.id or g.user.admin):
        reservation.cancelled = True
        db_session.commit()

        return jsonify({'success': True})
    else:
        return abort(400)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/')
def index():
    authenticated = g.user and g.user.is_authenticated
    if request.args.get('logged_in', False) and authenticated:
        session['last_login'] = g.user.last_login
        g.user.last_login = datetime.datetime.now()
        db_session.commit()

    template = 'index.html'
    if authenticated:
        template = 'reservations.html'

    return render_template(template, rooms=Room.query.all())

if __name__ == '__main__':
    manager.run()
