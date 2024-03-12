from ..extensions import db

class ApplicationKeyword(db.Model):
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), primary_key=True)
    application = db.relationship('Application', backref='keywords')
    keyword = db.relationship('Keyword', backref='applications')