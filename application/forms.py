from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, FloatField, SelectField, DateField, URLField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class CompanyForm(FlaskForm):
    name = StringField("Company Name", validators=[DataRequired()], render_kw={"placeholder": "Company Name"})
    url = StringField("Company URL", validators=[DataRequired()], render_kw={"placeholder": "Company URL"})
    career_page_url = StringField("Career Page URL", validators=[DataRequired()], render_kw={"placeholder": "Career Page URL"})
    description = TextAreaField("Description", render_kw={"placeholder": "Description"})
    types = StringField("Types",  render_kw={"placeholder": "Types"})
    city = StringField("City",  render_kw={"placeholder": "City"})
    state = StringField("State",  render_kw={"placeholder": "State"})
    country = StringField("Country", validators=[DataRequired()], render_kw={"placeholder": "Country"})
    submit = SubmitField("Add Company")


class FoodForm(FlaskForm):
    name = StringField("Food Name", validators=[DataRequired()], render_kw={"placeholder": "Food item name"})
    description = TextAreaField("Description", render_kw={"placeholder": "Description / Ingredients / How did you like it?"})
    price = FloatField("Price", validators=[DataRequired()], render_kw={"placeholder": "Price"})
    brand = StringField("Brand", render_kw={"placeholder": "Brand"})
    category = StringField("Category", render_kw={"placeholder": "Category"})
    city = StringField("City", validators=[DataRequired()], render_kw={"placeholder": "City"})
    state = StringField("State", validators=[DataRequired()], render_kw={"placeholder": "State"})
    country = StringField("Country", validators=[DataRequired()], render_kw={"placeholder": "Country"})
    image = FileField("Image File", 
                      validators=[FileRequired()], 
                      name="file-to-upload",
                      render_kw={"placeholder": "Image File", "accept": "image/*"})
    submit = SubmitField("Add Food")


class ApplicationForm(FlaskForm):
    company = StringField('Company Name', validators=[DataRequired()], render_kw={"placeholder": "Company Name"})
    position = StringField('Position / Title', render_kw={"placeholder": "Position / Title"})
    date = DateField('Date', render_kw={"placeholder": "Date"})
    link = URLField('Link to Job Posting', render_kw={"placeholder": "Link to Job Posting"})
    email_given = StringField('Email Given', validators=[DataRequired()], render_kw={"placeholder": "Email Given"})
    status = SelectField('Status', choices=[('applied', 'Applied'), ('interviewed', 'Interviewed'),
                                            ('rejected', 'Rejected'), ('offer', 'Offer'), ('none', 'None')],
                         validators=[DataRequired()], render_kw={"placeholder": "Status"})
    portal = SelectField('Portal', choices=[('linkedin', 'LinkedIn'), ('indeed', 'Indeed'),
                                           ('glassdoor', 'Glassdoor'), ('companyPortal', 'Company Portal'),
                                           ('other', 'Other')],
                        validators=[DataRequired()], render_kw={"placeholder": "Portal"})
    notes = TextAreaField('Notes', render_kw={"placeholder": "Notes"})
    submit = SubmitField('Submit')