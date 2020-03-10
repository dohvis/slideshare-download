from os.path import dirname, join as os_join, abspath

from celery import Celery
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import (
    Migrate,
    MigrateCommand,
)
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy, connection_stack
from sqlalchemy import event

BASE_DIR = os_join(dirname(dirname(abspath(__file__))))
TEMPLATES_DIR = os_join(BASE_DIR, 'templates')
MEDIA_DIR = os_join(BASE_DIR, 'media')
STATIC_DIR = os_join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=TEMPLATES_DIR)
db = SQLAlchemy()




def create_app():
    from project.controllers import downloader_bp
    app.config.from_pyfile('../config.py')
    app.secret_key = 'super secret key'
    app.register_blueprint(downloader_bp, url_prefix='/')
    db.init_app(app)
    return app


manager = Manager(app)
manager.add_command('db', MigrateCommand)

app = create_app()
db.init_app(app)

from project.models import *  # NOQA

admin = Admin(app)
admin.add_view(ModelView(Slide, db.session))
admin.add_view(ModelView(DownloadState, db.session))
migrate = Migrate(app, db)

app.config.from_pyfile('../config.py')  # for CELERY_BROKER_URL
celery = Celery(app.name, backend='amqp', broker=app.config['CELERY_BROKER_URL'])

from project.downloader.tasks import slide2img
celery.task(bind=True)(slide2img)


@event.listens_for(DownloadState, "before_insert")
def on_models_committed(mapper, connection, target):
    s2 = db.create_scoped_session({'scopefunc': connection_stack.__ident_func__})
    print(mapper, connection, target.idx)
    print(s2.query(DownloadState).all())
    s2.close()
