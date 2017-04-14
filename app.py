#!/usr/bin/env python3

import datetime

from setup import app, login_manager, db_session, manager
from models import Room, Reservation
from schemas import reservation_schema, reservations_schema
from utils import minify_html, inject_anlytics_tracking_id, inject_version, success, error
from utils.csrf import check_csrf_token, inject_csrf_token
from utils.users import load_user, global_user, inject_user

from flask import render_template, g, request, session, redirect, abort
from flask_login import logout_user, login_required

login_manager.user_loader(load_user)
app.before_request(global_user)

app.before_request(check_csrf_token)
app.context_processor(inject_csrf_token)
app.context_processor(inject_user)

app.after_request(minify_html)
app.context_processor(inject_anlytics_tracking_id)
app.context_processor(inject_version)

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
            return error('Invalid room number')

        start, end = datetime.datetime.utcfromtimestamp(int(start)), datetime.datetime.utcfromtimestamp(int(end))

        # TODO: Abstract validation to make edit_reservation easier
        starts_in_future = start > datetime.datetime.now()
        starts_in_near_future = starts_in_future and ((start - datetime.datetime.now()) <= datetime.timedelta(days=10))
        ends_after_start = end > start
        valid_duration = datetime.timedelta(minutes=30) <= (end - start) <= datetime.timedelta(hours=3)
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
            return success()
        else:
            return error('Invalid reservation time/duration')
    else:
        return error('Missing required inputs')

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

        return success()
    else:
        return error('Unauthorized to cancel that reservation' if reservation else 'Invalid reservation')

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
