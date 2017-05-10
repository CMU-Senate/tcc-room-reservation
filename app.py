#!/usr/bin/env python3

import datetime

from setup import app, login_manager, db_session, manager
from models import User, Room, Reservation
from schemas import reservation_schema, reservations_schema
from utils import (
    minify_html, success, error,
    start_end_required, admin_required, login_forbidden,
    inject_anlytics_tracking_id, inject_recaptcha_key, inject_version, inject_filters
)
from utils.csrf import check_csrf_token, inject_csrf_token
from utils.users import load_user, global_user, inject_user
from emails import contact_us

import requests
from flask import render_template, g, request, session, redirect, abort, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy.orm import joinedload

login_manager.user_loader(load_user)
app.before_request(global_user)

app.before_request(check_csrf_token)
app.context_processor(inject_csrf_token)
app.context_processor(inject_user)

app.after_request(minify_html)
app.context_processor(inject_anlytics_tracking_id)
app.context_processor(inject_recaptcha_key)
app.context_processor(inject_version)
app.context_processor(inject_filters)

@app.route('/reservations/<int:room>')
@login_required
@start_end_required
def get_reservations(room, start=None, end=None):
    room = db_session.query(Room).filter_by(id=room).first()
    if room:
        reservations = room.reservations.filter(
            Reservation.cancelled.in_([True, False] if g.user.admin else [False]) &
            (Reservation.start >= start) &
            (Reservation.end <= end)
        )
        return reservations_schema.jsonify(reservations)
    else:
        return error('Invalid room')

@app.route('/reservation/<int:reservation>')
@login_required
def get_reservation(reservation):
    reservation = db_session.query(Reservation).filter_by(id=reservation).first()
    if reservation:
        return reservation_schema.jsonify(reservation)
    else:
        return abort(404)

@app.route('/reservation/add', methods=['POST'])
@login_required
@start_end_required
def add_reservation(start=None, end=None):
    room = request.form.get('room', None)
    if not room:
        return error('Missing room')

    room = db_session.query(Room).filter_by(id=int(room)).first()
    if not room:
        return error('Invalid room')

    try:
        db_session.add(Reservation(
            user_id=g.user.id,
            room_id=room.id,
            start=start,
            end=end
        ))
        db_session.commit()
        return success()
    except AssertionError as e:
        db_session.rollback()
        return error(str(e))

@app.route('/reservation/<int:reservation>/edit', methods=['POST'])
@login_required
@start_end_required
def edit_reservation(reservation, start=None, end=None):
    reservation = db_session.query(Reservation).filter_by(id=reservation).first()
    if not reservation:
        return error('Invalid reservation')
    if not g.user.admin and reservation.user != g.user:
        return error('Unauthorized to edit that reservation')
    if reservation.start <= datetime.datetime.now():
        return error('Cannot edit reservation starting in the past')

    try:
        reservation.start = start
        reservation.end = end
        db_session.commit()
        return success()
    except AssertionError as e:
        db_session.rollback()
        return error(str(e))

@app.route('/reservation/<int:reservation>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation):
    reservation = db_session.query(Reservation).filter_by(id=reservation).first()
    if not reservation:
        return error('Invalid reservation')
    if reservation.start <= datetime.datetime.now():
        return error('Cannot edit reservation starting in the past')
    if not g.user.admin and reservation.user != g.user:
        return error('Unauthorized to cancel that reservation')

    reservation.cancelled = True
    db_session.commit()
    return success()

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    if request.method == 'GET':
        context = {
            'rooms': db_session.query(Room).all(),
            'users': db_session.query(User).all(),
            'sudo': app.config['SUDO_USERID'],
        }
        return render_template('admin.html', **context)
    else:
        room_id = request.form.get('id', None)
        if not room_id:
            return abort(400)

        room = db_session.query(Room).filter_by(id=room_id).first()
        if not room:
            return abort(400)

        room.name = request.form.get('name', '')
        room.description = request.form.get('description', '')
        room.reservable = bool(request.form.get('reservable'))
        db_session.commit()

        return redirect('/admin')

@app.route('/admin/ban-users', methods=['POST'])
@login_required
@admin_required
def ban_users():
    users = set(request.form.getlist('banned-users'))

    for user in db_session.query(User).filter(
        ((User.banned == True) & ~User.id.in_(users)) |
        ((User.banned == False) & User.id.in_(users))
    ).all(): # noqa: E712 (SQLAlchemy requires it)
        user.banned = user.id in users
    db_session.commit()

    flash('Updated list of banned users (%s users).' % len(users))
    return redirect('/admin')

@app.route('/admin/login-as', methods=['POST'])
@login_required
@admin_required
def login_as():
    user_id = request.form.get('id')
    if not user_id:
        return abort(400)

    user = db_session.query(User).filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id)
        db_session.add(user)
        db_session.commit()

    logout_user()
    login_user(user)
    flash('Logged in as %s.' % user.id)
    return redirect('/')

@app.route('/admin/set-admins', methods=['POST'])
@login_required
@admin_required
def add_admin():
    users = set(request.form.getlist('admins')) | set([app.config['SUDO_USERID']])
    if g.user.id not in users:
        flash('You may not remove your own administrative privileges.')
        return redirect('/admin')

    for user in db_session.query(User).filter(
        ((User.admin == True) & ~User.id.in_(users)) |
        ((User.admin == False) & User.id.in_(users))
    ).all(): # noqa: E712 (SQLAlchemy requires it)
        user.admin = user.id in users
    db_session.commit()

    flash('Updated list of admins: %s.' % ', '.join(users))
    return redirect('/admin')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/sudo', methods=['GET', 'POST'])
@login_forbidden
def sudo():
    if request.method == 'POST':
        if request.form.get('password') == app.config['config']['DEFAULT']['SUDO_ACCOUNT_PASSWORD']:
            sudo_user = db_session.query(User).filter_by(id=app.config['SUDO_USERID']).first()
            login_user(sudo_user)
            return redirect('/')
        flash('Incorrect password.')

    return render_template('sudo.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        recaptcha_response = request.form.get('g-recaptcha-response', None)
        if recaptcha_response:
            if not requests.post('https://www.google.com/recaptcha/api/siteverify', data={
                'secret': app.config['config']['DEFAULT']['RECAPTCHA_SECRET'],
                'response': recaptcha_response,
                'remoteip': request.remote_addr
            }).json()['success']:
                abort(403)
        else:
            abort(403)

        name = request.form.get('name')
        email = request.form.get('email')
        comments = request.form.get('comments')

        contact_us(name, email, comments)

        flash('Thank you for your feedback!')
        return redirect('/')

@app.route('/reservations')
@login_required
def reservations():
    reservations = db_session.query(Reservation).options(joinedload(Reservation.room))
    if not g.user.admin:
        reservations = reservations.filter_by(user=g.user)
    reservations = reservations.all()

    return render_template('reservations.html', reservations=reservations, now=datetime.datetime.now())

@app.route('/')
def index():
    authenticated = g.user and g.user.is_authenticated
    if request.args.get('logged_in', False) and authenticated:
        session['last_login'] = g.user.last_login
        g.user.last_login = datetime.datetime.now()
        db_session.commit()

    template = 'index.html'
    if authenticated:
        template = 'calendar.html'

    return render_template(template, rooms=db_session.query(Room).all(), config=app.config['config'])

if __name__ == '__main__':
    manager.run()
