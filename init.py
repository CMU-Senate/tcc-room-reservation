from flask_script import Command
from social_flask_sqlalchemy import models

class Init(Command):
    '''initialize database'''

    def run(self):
        from setup import db, db_session, engine, app
        from models import Room, User

        models.PSABase.metadata.create_all(engine)
        db.create_all()
        db_session.commit()

        db_session.add(Room(name='Glass Room 1', reservable=True))
        db_session.add(Room(name='Glass Room 2', reservable=False))
        db_session.add(User(id=app.config['SUDO_USERID'], admin=True))
        db_session.commit()
