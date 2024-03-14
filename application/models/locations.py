from ..extensions import db

class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default=db.func.now())
    date_updated = db.Column(db.DateTime, default=db.func.now())
    deleted = db.Column(db.Boolean, default=False)