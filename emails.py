#!/usr/bin/env python3

import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from setup import app, db_session
from models import Reservation

emails = Path('emails')
config = app.config['config']['EMAILS']

def setup_message(subject, to, text, html):
    message = MIMEMultipart('alternative')

    message['Subject'] = subject
    message['From'] = config['SMTP_EMAIL']
    message['To'] = to

    message.attach(text)
    message.attach(html)

    return message

def fill_template(template_name, **kwargs):
    with open(emails / f'{template_name}.html') as html_template, open(emails / f'{template_name}.txt') as text_template:
        return (
            MIMEText(text_template.read().format(**kwargs()), 'plain'),
            MIMEText(html_template.read().format(**kwargs()), 'html')
        )

def send(to, message):
    with smtplib.SMTP('localhost') as smtp:
        smtp.sendmail(config['SMTP_EMAIL'], [to], message.as_string())

def contact_us(name, email, comments, subject='TCC Reservation System Feedback'):
    text, html = fill_template('contact_us', name=name, email=email, comments=comments)

    message = setup_message(subject, config['CONTACT_EMAIL'], text, html)
    message.add_header('reply-to', email)

    send(config['CONTACT_EMAIL'], message)

def reservation_base(template, subject, reservation):
    text, html = fill_template(template, start=reservation.start, end=reservation.end)
    message = setup_message(subject, reservation.user.email(), text, html)
    send(reservation.user.email(), message)

def reservation_reminder(reservation):
    reservation_base('reminder', 'TCC Reservation Reminder', reservation)

def reservation_confirmed(reservation):
    reservation_base('confirmation', 'TCC Reservation Confirmation', reservation)

def reservation_edited(reservation):
    reservation_base('edit', 'TCC Reservation Edited', reservation)

def reservation_cancelled(reservation):
    reservation_base('cancellation', 'TCC Reservation Cancelled', reservation)

def main():
    reminder_time = datetime.datetime.now() - datetime.timedelta(minutes=config['REMINDER_TIME_MINUTES'])
    reservations = db_session.query(Reservation).filter_by(
        (Reservation.reminded == False) & # noqa: E712
        Reservation.start >= reminder_time
    ).all()

    for reservation in reservations:
        reservation.reminded = True
        reservation_reminder(reservation)
        db_session.commit()

if __name__ == '__main__':
    main()
