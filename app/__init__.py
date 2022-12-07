import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_scheduler.flask_scheduler import FlaskScheduler

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

from . import views
app.register_blueprint(views.bp)

from app.populate import *

scheduler = FlaskScheduler(timezone="Europe/Warsaw", minutes=0, hours=1, seconds=0)

from app.jobs import *

scheduler.init_app(app)
scheduler.start()
