from project import db
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

users_slides = db.Table(
    'users_slides',
    db.Column("user_id", db.Integer, db.ForeignKey("user.idx")),
    db.Column("slide_id", db.Integer, db.ForeignKey("slide.idx")),
)


class DownloadState(db.Model):
    __tablename__ = "download_state"
    idx = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(255), unique=True)
    number_of_images = db.Column(db.Integer())
    downloading_image = db.Column(db.Integer(), default=0)
    slide = db.ForeignKey("Slide")


class Slide(db.Model):
    __tablename__ = "slide"
    idx = db.Column(db.Integer(), primary_key=True)
    slideshare_url = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(64))
    author = db.Column(db.String(64))
    description = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    views = db.Column(db.Integer, default=0)
    _hash = db.Column(db.String(32))

    def __init__(self, slideshare_url, thumbnail=None, pdf_path=None):
        self.slideshare_url = slideshare_url
        self.thumbnail = thumbnail
        self.pdf_path = pdf_path

    @staticmethod
    def get_or_create(url):
        instance = Slide.query.filter_by(slideshare_url=url).first()
        if instance:
            return instance, True
        s = Slide(url)
        db.session.add(s)
        db.session.commit()
        return s, False


class User(db.Model):
    from datetime import datetime
    __tablename__ = "user"
    idx = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(255))
    fb_id = db.Column(db.String(30), unique=True)
    is_active = db.Column(db.BOOLEAN, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    slides = db.relationship('Slide', secondary=users_slides, backref='users')

    def __init__(self, email, password, fb_id=None):
        self.email = email
        self.set_password(password)
        self.fb_id = fb_id

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
