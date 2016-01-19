from .. import db
from ..utils import get_hash_of_file


class Slide(db.Model):
    __tablename__ = "slide"
    idx = db.Column(db.Integer(), primary_key=True)
    slideshare_url = db.Column(db.String(255))
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

    @staticmethod
    def get_hash_of_pdf(url):
        from os.path import join
        from .. import MEDIA_DIR
        s = Slide.query.filter_by(slideshare_url=url).first()
        s._hash = get_hash_of_file(join(MEDIA_DIR, s.pdf_path))
        db.session.commit()
