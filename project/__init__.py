from os.path import join, abspath, dirname

from celery import Celery
from flask import (
    Flask,
)
from flask.ext.sqlalchemy import SQLAlchemy


BASE_DIR = dirname(abspath(__file__))

TEMPLATE_DIR = join(BASE_DIR, 'templates')
STATIC_DIR = join(BASE_DIR, 'static')
MEDIA_DIR = join(BASE_DIR, 'media')

app = Flask(__name__)
db = SQLAlchemy(app)


def create_app():
    from .accounts import account_bp
    app.config.from_pyfile('../config.cfg')
    app.register_blueprint(account_bp, url_prefix='/accounts')
    return app


app = create_app()
db = SQLAlchemy(app).init_app(app)
celery = Celery(app.name, backend='amqp', broker=app.config['CELERY_BROKER_URL'])
from .slides.core import slide2img
celery.task(bind=True)(slide2img)
