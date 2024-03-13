from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, FloatField, SelectField, DateField, URLField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired


class CompanyForm(FlaskForm):
    name = StringField("Company Name", validators=[DataRequired()], render_kw={"placeholder": "Company Name"})
    url = StringField("Company URL", render_kw={"placeholder": "Company URL"})
    career_page_url = StringField("Career Page URL", render_kw={"placeholder": "Career Page URL"})
    description = TextAreaField("Description", render_kw={"placeholder": "Description"})
    types = StringField("Types",  render_kw={"placeholder": "Types"})
    
    country = StringField("Country", render_kw={"placeholder": "Country"})
    state = StringField("State",  render_kw={"placeholder": "State"})
    city = StringField("City",  render_kw={"placeholder": "City"})
    
    submit = SubmitField("Add Company")


class FoodForm(FlaskForm):
    name = StringField("Food Name", validators=[DataRequired()], render_kw={"placeholder": "Food item name"})
    description = TextAreaField("Description", render_kw={"placeholder": "Description / Ingredients / How did you like it?"})
    price = FloatField("Price", validators=[DataRequired()], render_kw={"placeholder": "Price"})
    brand = StringField("Brand", render_kw={"placeholder": "Brand"})
    category = StringField("Category", render_kw={"placeholder": "Category"})
    
    country = StringField("Country", validators=[DataRequired()], render_kw={"placeholder": "Country"})
    state = StringField("State", validators=[DataRequired()], render_kw={"placeholder": "State"})
    city = StringField("City", validators=[DataRequired()], render_kw={"placeholder": "City"})
    
    image = FileField("Image File", 
                      name="file-to-upload",
                      render_kw={"placeholder": "Image File", "accept": "image/*"})
    submit = SubmitField("Add Food")


class ApplicationForm(FlaskForm):
    company = StringField('Company Name', validators=[DataRequired()], render_kw={"placeholder": "Company Name"})
    position = StringField('Position / Title', render_kw={"placeholder": "Position / Title"})
    date = DateField('Date', render_kw={"placeholder": "Date"})
    link = URLField('Link to Job Posting', render_kw={"placeholder": "Link to Job Posting"})
    email_given = SelectField('Email Given', choices=[('Outlook', 'Outlook'), ('Gmail', 'Gmail'), ('Proton', 'Proton'), ('Other', 'Other')])
    status = SelectField('Status', choices=[('Applied', 'Applied'), ('Interviewed', 'Interviewed'),
                                            ('Not Selected', 'Not Selected'), ('Offer', 'Offer'), ('None', 'None')],
                         validators=[DataRequired()], render_kw={"placeholder": "Status"})
    portal = SelectField('Portal', choices=[('LinkedIn', 'LinkedIn'), ('Indeed', 'Indeed'),
                                           ('Glassdoor', 'Glassdoor'), ('Company Portal', 'Company Portal'),
                                           ('Other', 'Other')],
                        validators=[DataRequired()], render_kw={"placeholder": "Portal"})
    notes = TextAreaField('Notes', render_kw={"placeholder": "Notes"})
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()], render_kw={"placeholder": "Username"})
    password = PasswordField("Password", validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class WeightTrackerForm(FlaskForm):
    weight = FloatField("Weight", validators=[DataRequired()], render_kw={"placeholder": "Weight"})
    date = DateField("Date", render_kw={"placeholder": "Date"})
    submit = SubmitField("Submit")