from flask import Flask, render_template, request as req, send_from_directory, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, Server
from flask.ext.migrate import Migrate, MigrateCommand
from celery import Celery
from os import path, walk, system, makedirs
from os.path import join, abspath

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

MEDIA = '/tmp/slideshare-vpn/'
TEMPLATE_DIR = path.join(path.dirname(path.abspath(__file__)), 'templates')
STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), 'static')
app = Flask(__name__, template_folder=TEMPLATE_DIR)


def create_app():
    app.config.from_pyfile('config.cfg')
    return app

app = create_app()
db = SQLAlchemy(app)
print(app.config['CELERY_BROKER_URL'])
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])


users_slides = db.Table('users_slides',
    db.Column("user_id", db.Integer, db.ForeignKey("user.idx")),
    db.Column("slide_id", db.Integer, db.ForeignKey("slide.idx"))
    )


class User(db.Model):
    from datetime import datetime
    __tablename__ = "user"
    idx = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(64))
    pw = db.Column(db.String(32))
    name = db.Column(db.String(32))
    fb_id = db.Column(db.String(30), unique=True)
    is_active = db.Column(db.BOOLEAN, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    slides = db.relationship('Slide', secondary=users_slides, backref='users')

    def __init__(self, email, pw, name,  fb_id=None):
        self.email = email
        self.pw = pw
        self.name = name
        self.fb_id = fb_id


class Slide(db.Model):
    __tablename__ = "slide"
    idx = db.Column(db.Integer(), primary_key=True)
    slideshare_url = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    pdf_path = db.Column(db.String)
    views = db.Column(db.Integer, default=0)

    def __init__(self, slideshare_url, thumbnail, pdf_path):
        self.slideshare_url = slideshare_url
        self.thumbnail = thumbnail
        self.pdf_path = pdf_path


migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command('run', Server(host='0.0.0.0', port=5000))

@manager.command
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)

    for line in sorted(output):
        print(line)


@app.route('/static/<path:filename>')
def static_serving(filename):
    return send_from_directory(STATIC_DIR, filename)


def get_dir_files(title):
    files = []
    for (dirpath, dirnames, filenames) in walk(join('/tmp/slideshare-vpn/', title)): # TODO string to media
        # print(dirpath, filenames)
        for f in filenames:
            files.append(abspath(join(dirpath, f)))
        break
    return files


def convert_pdf(title):
    from img2pdf import convert
    from natsort import natsorted
    files = natsorted(get_dir_files(title))
    print(files)
    pdf_bytes = convert(files, dpi=300, x=None, y=None)
    with open('%s.pdf' % title, 'wb') as doc:
        doc.write(pdf_bytes)


@celery.task(bind=True)
def slide2img(self, url):
    from bs4 import BeautifulSoup
    from urllib import request

    html = request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string
    title = title.replace(" ", "-")
    print(title)
    images = soup.findAll('img', {'class': 'slide_image'})

    saved_dir = join(MEDIA, title)
    makedirs(saved_dir, exist_ok=True)  # Only python >= 3.2

    for i, image in enumerate(images):
        image_url = image['data-full'].split('?')[0]
        command = 'wget %s -O %s.jpg --quiet' % (image_url, join(saved_dir, str(i)))
        print("command : %s" % command)
        self.update_state(state='PROGRESS')
        system(command)

    convert_pdf(title)
    return title


@app.route("/", methods=['GET', 'POST'])
def index():
    if req.method == 'GET':
        return render_template('index.html')
    else:
        slide2img.apply_async((req.form['url'],))
    return "done!"


@app.route("/result", methods=['GET'])
def result():
    return render_template('result.html')


if __name__ == "__main__":
    manager.run()
