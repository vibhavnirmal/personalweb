from ..extensions import db

class Keyword(db.Model):
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String, nullable=False)
    frequency = db.Column(db.Integer, default=0)
    jobid = db.Column(db.Integer, db.ForeignKey('applications.id'))

