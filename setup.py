import subprocess
import sys
import configparser
import os

from init import Init

from flask import Flask
from flask_bower import Bower
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_script import Server, Manager, Shell
from flask_marshmallow import Marshmallow
from social_flask.routes import social_auth
from social_flask_sqlalchemy.models import init_social
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_assets import Environment

app = Flask(__name__)

cwd = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(os.path.join(cwd, 'settings.cfg'))
app.config['config'] = config
config = config['DEFAULT']

app.config['DEBUG'] = config.getboolean('DEBUG')
app.config['ASSETS_DEBUG'] = app.config['DEBUG']
app.config['SQLALCHEMY_DATABASE_URI'] = config['DB_PATH']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

ma = Marshmallow(app)

manager = Manager(app)
manager.add_command('runserver', Server())
manager.add_command('shell', Shell(make_context=lambda: {
    'app': app,
    'db_session': db_session
}))
manager.add_command('init', Init())

Bower(app)
environment = Environment(app)
environment.append_path('static')
environment.append_path('bower_components')

version = subprocess.check_output(['git', 'describe', '--tags'], cwd=cwd).decode(sys.stdout.encoding).strip()

app.config['GOOGLE_ANALYTICS_TRACKING_ID'] = config['GOOGLE_ANALYTICS_TRACKING_ID']

app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['SESSION_PROTECTION'] = 'strong'
app.config['SOCIAL_AUTH_LOGIN_URL'] = '/login'
app.config['SOCIAL_AUTH_LOGIN_REDIRECT_URL'] = '/?logged_in=1'
app.config['SOCIAL_AUTH_USER_MODEL'] = 'models.User'
app.config['SOCIAL_AUTH_AUTHENTICATION_BACKENDS'] = ('social_core.backends.google.GoogleOAuth2', )
app.config['SOCIAL_AUTH_FIELDS_STORED_IN_SESSION'] = ['keep']
app.config['SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS'] = {
    'hd': 'andrew.cmu.edu',
    'access_type': 'online',
    'approval_prompt': 'auto'
}
app.config['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'] = config['GOOGLE_OATH2_CLIENT_ID']
app.config['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'] = config['GOOGLE_OATH2_SECRET']

app.register_blueprint(social_auth)
init_social(app, db_session)

login_manager = LoginManager()
login_manager.login_view = 'index'
login_manager.login_message = 'Please login to access that page.'
login_manager.init_app(app)

app.config['SMTP_EMAIL'] = config['SMTP_EMAIL']
app.config['CONTACT_EMAIL'] = config['CONTACT_EMAIL']
