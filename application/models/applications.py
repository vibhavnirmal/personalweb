from ..extensions import db

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    company = db.relationship('Company', backref='applications')
    
    date_added = db.Column(db.DateTime, default=db.func.now())
    date_updated = db.Column(db.DateTime, default=db.func.now())
    deleted = db.Column(db.Boolean, default=False)
    link = db.Column(db.String)
    email_used = db.Column(db.String)
    status = db.Column(db.String)
    from_portal = db.Column(db.String)
    salary_low = db.Column(db.Integer)
    salary_high = db.Column(db.Integer)
    
    description = db.Column(db.String(255))
    personal_notes = db.Column(db.String(255))