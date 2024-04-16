from ..extensions import db

class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String, nullable=False)

    logo = db.Column(db.String)

    linkedin = db.Column(db.Text)
    website = db.Column(db.Text)
    careers_page = db.Column(db.Text)

    location = db.Column(db.Text)
    
    about = db.Column(db.Text)

    types = db.Column(db.Text)
    industry = db.Column(db.String)

    date_added = db.Column(db.Date, default=db.func.now())
    date_updated = db.Column(db.Date, default=db.func.now())
    
    deleted = db.Column(db.Boolean)

    def __repr__(self):
        return '<Company %r>' % self.company_name
    
    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
