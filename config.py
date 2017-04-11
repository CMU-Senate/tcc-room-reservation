import subprocess
import sys

from flask import Flask

from flask_bower import Bower
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from social_flask.routes import social_auth
from social_flask_sqlalchemy.models import init_social
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Bower(app)

version = subprocess.check_output(['git', 'describe', '--tags']).decode(sys.stdout.encoding).strip()

app.config['GOOGLE_ANALYTICS_TRACKING_ID'] = ''

app.config['SECRET_KEY'] = 'development'
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

google_oath2_client_id = ''
google_oauth2_secret = ''

app.config['SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'] = google_oath2_client_id
app.config['SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'] = google_oauth2_secret

app.register_blueprint(social_auth)
init_social(app, db_session)

login_manager = LoginManager()
login_manager.login_view = 'index'
login_manager.login_message = 'Please login to access that page.'
login_manager.init_app(app)

app.config['SMTP_EMAIL'] = 'sushain@cs.cmu.edu'
app.config['CONTACT_EMAIL'] = 'sushain@cs.cmu.edu'
