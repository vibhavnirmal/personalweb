from ..extensions import db


class Keyword(db.Model):
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String, nullable=False, unique=True)
    frequency = db.Column(db.Integer, default=0)

    # Define the relationship to applications
    applications = db.relationship('Application', secondary='keyword_association', backref='keywords')

    def __repr__(self):
        return '<Keyword %r>' % self.keyword

class KeywordAssociation(db.Model):
    __tablename__ = "keyword_association"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'))
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))

    def __repr__(self):
        return '<KeywordAssociation %r>' % self.id