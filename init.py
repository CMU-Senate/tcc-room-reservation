from flask_script import Command
from social_flask_sqlalchemy import models

class Init(Command):
    '''initialize database'''

    def run(self):
        from setup import db, db_session, engine

        models.PSABase.metadata.create_all(engine)
        db.create_all()

        db_session.commit()
