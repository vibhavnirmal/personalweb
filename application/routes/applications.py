from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..extensions import db

from ..models.applications import Application
from ..models.companies import Company
from ..models.locations import Location

from ..forms import ApplicationForm

from sqlalchemy.orm import joinedload
import json
from datetime import datetime

my_applications = Blueprint('my_applications', __name__, url_prefix='/applications')

@my_applications.route('/view_applications', methods=['GET'])
def view_applications():
    all_data = Application.query.options(joinedload(Application.company)).all()

    for application in all_data:
        application.date_added = application.date_added.strftime("%m/%d/%Y")

    return render_template('view_applications.html', title='View Applications', files=all_data)

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
            application.date_added = datetime.strptime(str(form.date.data), '%Y-%m-%d')
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