from .. import db

users_slides = db.Table(
        'users_slides',
        db.Column("user_id", db.Integer, db.ForeignKey("user.idx")),
        db.Column("slide_id", db.Integer, db.ForeignKey("slide.idx"))
)


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
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash, generate_password_hash
        return check_password_hash(self.password, password)
