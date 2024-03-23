from flask import Blueprint, render_template, request, redirect, url_for, flash, abort

from ..utils import insert_keywords, get_all_company_names, get_company_id
from ..extensions import db

from ..models.applications import Application

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
        application.date_added = application.date_added.strftime("%Y-%m-%d")

    return render_template('application/view_applications.html', title='View Applications', files=all_data, company_name=company_name)


@my_applications.route('/add_application', methods=['POST', 'GET'])
def add_application():
    form = ApplicationForm()

    if form.validate_on_submit():
        new_application = Application(
            position=form.position.data.replace("/", "-"),
            date_added=form.date.data,
            link=form.link.data,
            email_used=form.email_given.data,
            status=form.status.data,
            from_portal=form.portal.data,
            description=form.notes.data,
            deleted=False,
            company_id=get_company_id(form.company.data)
        )

        db.session.add(new_application)
        db.session.commit()

        insert_keywords(new_application.id, form.notes.data)

        return redirect(url_for('my_applications.view_applications'))

    companies = json.dumps(get_all_company_names())
    return render_template('application/add_application.html', title='Add Application', form=form, companies=companies)

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
    return render_template('application/edit_application.html', title='Edit Application', form=form, companies=companies)

@my_applications.route('/delete_application', methods=['POST','GET'])
def delete_application():
    application_id = request.args.get('id')
    application = Application.query.filter_by(id=application_id).first()
    application.deleted = True
    db.session.commit()

    return redirect(url_for('my_applications.view_applications'))