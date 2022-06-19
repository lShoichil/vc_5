from web import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50))
    name = db.Column(db.String(50))
    admin = db.Column(db.Boolean)
    password = db.Column(db.String(80))


class Mems(db.Model):
    __tablename__ = "mems"
    id = db.Column(db.Integer, primary_key=True)
    vk_links = db.Column(db.String(300))
    vk_id = db.Column(db.Integer)
    likes_parse = db.Column(db.Integer)
    likes_count = db.Column(db.Integer)
    url_image = db.Column(db.String(300))