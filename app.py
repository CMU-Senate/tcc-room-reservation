#!/usr/bin/env python3

import datetime
import smtplib
import textwrap
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from setup import app, login_manager, db_session, manager
from models import Room, Reservation
from schemas import reservation_schema, reservations_schema
from utils import minify_html, inject_anlytics_tracking_id, inject_version, inject_filters, success, error
from utils.csrf import check_csrf_token, inject_csrf_token
from utils.users import load_user, global_user, inject_user

from flask import render_template, g, request, session, redirect, abort, flash
from flask_login import logout_user, login_required

login_manager.user_loader(load_user)
app.before_request(global_user)

app.before_request(check_csrf_token)
app.context_processor(inject_csrf_token)
app.context_processor(inject_user)

app.after_request(minify_html)
app.context_processor(inject_anlytics_tracking_id)
app.context_processor(inject_version)
app.context_processor(inject_filters)

@app.route('/reservations/<int:room>')
@login_required
def get_reservations(room):
    room = db_session.query(Room).filter_by(id=room).first()
    if room:
        reservations = room.reservations.filter(Reservation.cancelled.in_([True, False] if g.user.admin else [False]))
        return reservations_schema.jsonify(reservations)
    else:
        return abort(404)

@app.route('/reservation/<int:reservation>')
@login_required
def get_reservation(reservation):
    reservation = db_session.query(Reservation).filter(id == reservation).first()
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
        room = db_session.query(Room).filter_by(id=int(room)).first()
        if not room:
            return error('Invalid room')

        start, end = datetime.datetime.utcfromtimestamp(int(start)), datetime.datetime.utcfromtimestamp(int(end))

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
    else:
        return error('Missing required inputs')

@app.route('/reservation/<int:reservation>/edit', methods=['POST'])
@login_required
def edit_reservation(reservation):
    start, end = request.form.get('start', None), request.form.get('end', None)
    if start and end and reservation:
        reservation = db_session.query(Reservation).filter_by(id=reservation).first()
        if not reservation:
            return error('Invalid reservation')

        start, end = datetime.datetime.utcfromtimestamp(int(start)), datetime.datetime.utcfromtimestamp(int(end))

        try:
            reservation.start = start
            reservation.end = end
            db_session.commit()
            return success()
        except AssertionError as e:
            db_session.rollback()
            return error(str(e))
    else:
        return error('Missing required inputs')

@app.route('/reservation/<int:reservation>/cancel', methods=['POST'])
@login_required
def cancel_reservation(reservation):
    reservation = db_session.query(Reservation).filter_by(id=reservation).first()
    if reservation and (reservation.user.id == g.user.id or g.user.admin):
        reservation.cancelled = True
        db_session.commit()

        return success()
    else:
        return error('Unauthorized to cancel that reservation' if reservation else 'Invalid reservation')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        comments = request.form.get('comments')

        message = MIMEMultipart('alternative')
        text = MIMEText(textwrap.dedent(
            '''
                From: %s<%s>
                Body:
                > %s
            ''' % (name, email, comments)
        ), 'plain')
        html = MIMEText(textwrap.dedent(
            '''
                <b>From</b>: %s<%s><br>
                <b>Body</b>:<br>
                    <blockquote></blockquote>%s
                ''' % (name, email, comments)
        ), 'html')

        message['Subject'] = 'TCC Reservation System Feedback'
        message['From'] = app.config['SMTP_EMAIL']
        message['To'] = app.config['CONTACT_EMAIL']
        message.add_header('reply-to', email)

        message.attach(text)
        message.attach(html)

        s = smtplib.SMTP('localhost')
        s.sendmail(app.config['SMTP_EMAIL'], [app.config['CONTACT_EMAIL']], message.as_string())
        s.quit()

        flash('Thank you for your feedback!')
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

    return render_template(template, rooms=db_session.query(Room).all(), config=app.config['config'])

if __name__ == '__main__':
    manager.run()
