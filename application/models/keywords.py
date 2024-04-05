from ..extensions import db


class Keyword(db.Model):
    __tablename__ = "keywords"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False, unique=True, index=True)
    frequency = db.Column(db.Integer, default=0)
    deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<Keyword %r>' % self.keyword

class KeywordAssociation(db.Model):
    __tablename__ = "keyword_association"

    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'))
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))

    keyword = db.relationship('Keyword', backref='keyword_associations')
    application = db.relationship('Application', backref='keyword_associations')

    def __repr__(self):
        return '<KeywordAssociation %r>' % self.id