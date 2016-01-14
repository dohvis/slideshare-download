from .. import db


class Slide(db.Model):
    __tablename__ = "slide"
    idx = db.Column(db.Integer(), primary_key=True)
    slideshare_url = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    views = db.Column(db.Integer, default=0)

    def __init__(self, slideshare_url, thumbnail, pdf_path):
        self.slideshare_url = slideshare_url
        self.thumbnail = thumbnail
        self.pdf_path = pdf_path
