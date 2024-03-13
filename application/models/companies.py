from ..extensions import db

class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String, nullable=False)
    website = db.Column(db.String, nullable=False)
    careers_page = db.Column(db.String)

    # location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    # location = db.relationship('Location', backref='companies')

    location = db.Column(db.Text, nullable=False)
    
    about = db.Column(db.Text, nullable=False)
    types = db.Column(db.String, nullable=False)
    industry = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime, default=db.func.now())
    date_updated = db.Column(db.DateTime, default=db.func.now())
    deleted = db.Column(db.Boolean, default=False)