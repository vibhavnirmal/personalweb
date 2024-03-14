from ..extensions import db

class Weights(db.Model):
    __tablename__ = "weights"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    weight = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, default=db.func.now())