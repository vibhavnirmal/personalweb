from flask import Blueprint, render_template, request, redirect, url_for, flash
import ollama

# check if ollama installed
try:
    from ollama import generate
    ollama_available = True
except:
    print("Ollama not installed")
    ollama_available = False

from ..extensions import db

from ..models.applications import Application
from ..models.companies import Company
from ..models.keywords import Keyword

from ..forms import ApplicationForm

from sqlalchemy.orm import joinedload
import json
from datetime import datetime

my_applications = Blueprint('my_applications', __name__, url_prefix='/applications')

@my_applications.route('/view_applications', methods=['POST', 'GET'])
def view_applications(company_name=None):
    company_name = request.args.get('company_name')

    all_data = Application.query.options(joinedload(Application.company)).all()

    for application in all_data:
        application.date_added = application.date_added.strftime("%m/%d/%Y")

    return render_template('view_applications.html', title='View Applications', files=all_data, company_name=company_name)


@my_applications.route('/add_application', methods=['POST', 'GET'])
def add_application():
    form = ApplicationForm()  # Initialize form upfront

    if request.method == 'POST':
        if form.validate_on_submit():
            new_application = Application(
                position=form.position.data.replace("/", "-"),  # Combine assignment and replacement
                date_added=datetime.strptime(str(form.date.data), '%Y-%m-%d'),
                link=form.link.data,
                email_used=form.email_given.data,
                status=form.status.data,
                from_portal=form.portal.data,
                description=form.notes.data,
                deleted=False,
                company_id=get_company_id(form.company.data)  # Add company_id efficiently
            )

            if ollama_available:
                keywords_from_notes = generate_keywords(form.notes.data)
                print(keywords_from_notes)

                if len(keywords_from_notes) > 0:
                    for keyword in keywords_from_notes:
                        keyword_exists = Keyword.query.filter_by(keyword=keyword).first()
                        if keyword_exists:
                            keyword_exists.frequency += 1
                        else:
                            new_keyword = Keyword(keyword=keyword, frequency=1)
                            db.session.add(new_keyword)
                        db.session.commit()
            else:
                print("Ollama not installed")
                print("No keywords generated")

            db.session.add(new_application)
            db.session.commit()

            return redirect(url_for('my_applications.view_applications'))

    companies = json.dumps(get_all_company_names())  # Combine company retrieval and JSON conversion
    return render_template('add_application.html', title='Add Application', form=form, companies=companies)

@my_applications.route('/edit_application', methods=['POST','GET'])
def edit_application():
    if request.method == 'POST':
        form = ApplicationForm(request.form)
        if form.validate_on_submit():
            application_id = request.args.get('id')
            
            application = Application.query.filter_by(id=application_id).first()

            application.position = form.position.data.replace("/", "-")
            
            application.date_added = datetime.strptime(str(form.date.data), '%Y-%m-%d').date()
            application.date_updated = datetime.now().date()

            application.link = form.link.data
            application.email_used = form.email_given.data
            application.status = form.status.data
            application.from_portal = form.portal.data
            application.description = form.notes.data
            application.company_id = get_company_id(form.company.data)
        
            db.session.commit()
                    
        return redirect(url_for('my_applications.view_applications'))
    else:
        form = ApplicationForm()

        application_id = request.args.get('id')
        application = Application.query.filter_by(id=application_id).first()

        form.position.data = application.position.replace("-", "/")
        form.date.data = application.date_added
        form.link.data = application.link
        form.email_given.data = application.email_used
        form.status.data = application.status
        form.portal.data = application.from_portal
        form.notes.data = application.description
        form.company.data = application.company.company_name

    companies = json.dumps(get_all_company_names())
    return render_template('edit_application.html', title='Edit Application', form=form, companies=companies)

@my_applications.route('/delete_application', methods=['POST','GET'])
def delete_application():
    application_id = request.args.get('id')
    application = Application.query.filter_by(id=application_id).first()
    application.deleted = True
    db.session.commit()

    return redirect(url_for('my_applications.view_applications'))

def get_company_id(name):
    company_id = db.session.query(Company.id).filter_by(company_name=name).first()
    if company_id is None:
        company = Company(company_name=name)
        db.session.add(company)
        db.session.commit()
        return company.id
    else:
        return company_id[0]
    
def get_all_company_names():
    column_values = list(db.session.query(Company.company_name).all())
    names = [value[0] for value in column_values]
    return names

def preprocess_data(text):
    text = ''.join(map(lambda x: x.lower(), text))
    text = text.replace("\n", " ")
    # remove leading/trailing whitespace
    text = text.strip()
    
    return text

def generate_keywords(notes):
    my_prompt = "[INST] Generate comma separated keywords from the given job description. Keywords should not contain more than 3 words. \n\n" + notes + "\n\n [/INST]"

    if len(notes) < 50:
        return []

    if ollama_available:
        response = generate('mistral', my_prompt)
        keywords = response['response']

        # Use set comprehension for keyword preprocessing
        setOfKeywords = {preprocess_data(kw) for kw in keywords.split(",")}
        
        return setOfKeywords
    else:
        return []
