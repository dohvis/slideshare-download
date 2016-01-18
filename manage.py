from flask import (
    url_for,
)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from project import app, db
from project.accounts.models import User
from project.slides.models import Slide

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command('run', Server(host='0.0.0.0', port=5000))


@manager.command
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = "{:50s} {:20s} {}".format(rule.endpoint, methods, url)
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def create_all():
    db.create_all()

try:
    from .project.views import (
        index,
        result,
        static_serving,
        media_serving,
        get_status
    )
    from .project.slides.core import slide2img
    from .project import celery
except SystemError:
    from project.views import (
        index,
        result,
        static_serving,
        media_serving,
        get_status,
        redirect_real_path,
    )
    from project.slides.core import slide2img
    from project import celery
if __name__ == "__main__":
    app.route('/', methods=['GET', 'POST'])(index)
    app.route('/state/')(result)
    app.route('/api/state/')(get_status)
    app.route('/api/serve/<string:_hash>')(redirect_real_path)
    app.route('/static/<path:filename>')(static_serving)
    app.route('/media/<path:filename>')(media_serving)
    admin = Admin(app, name='slideshare-downloader', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Slide, db.session))
    manager.run()
