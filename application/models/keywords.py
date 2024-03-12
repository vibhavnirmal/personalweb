from ..extensions import db

class Keyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String, nullable=False)
    frequency = db.Column(db.Integer, default=0)

