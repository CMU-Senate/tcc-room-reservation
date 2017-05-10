#!/usr/bin/env python3

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from setup import app

emails = Path('emails')

def setup_message(subject, to, text, html):
    message = MIMEMultipart('alternative')

    message['Subject'] = subject
    message['From'] = app.config['SMTP_EMAIL']
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

def contact_us(name, email, comments, subject='TCC Reservation System Feedback'):
    text, html = fill_template('contact_us', name=name, email=email, comments=comments)

    message = setup_message(subject, app.config['CONTACT_EMAIL'], text, html)
    message.add_header('reply-to', email)

    with smtplib.SMTP('localhost') as smtp:
        smtp.sendmail(app.config['SMTP_EMAIL'], [app.config['CONTACT_EMAIL']], message.as_string())

def reservation_reminder(user):
    pass

def reservation_confirmed(user):
    pass

def reservation_edited(user):
    pass

def reservation_cancelled(user):
    pass

def main():
    pass

if __name__ == '__main__':
    main()
