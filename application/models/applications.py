from ..extensions import db

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Text, nullable=False)
    
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    company = db.relationship('Company', backref='applications')
    
    date_added = db.Column(db.Date, default=db.func.now())
    date_updated = db.Column(db.Date, default=db.func.now())

    deleted = db.Column(db.Boolean, default=False)

    link = db.Column(db.Text)
    email_used = db.Column(db.String)
    status = db.Column(db.String)

    from_portal = db.Column(db.String)

    salary_low = db.Column(db.String)
    salary_high = db.Column(db.String)
    
    description = db.Column(db.Text)
    personal_notes = db.Column(db.Text)

    def __repr__(self):
        return '<Application %r>' % self.position