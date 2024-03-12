from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..extensions import db

from ..models.applications import Application
from ..models.companies import Company

from ..forms import CompanyForm
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from datetime import datetime

my_companies = Blueprint('my_companies', __name__, url_prefix='/companies')

def countAppsPerCompany():
    all_data = Application.query.options(joinedload(Application.company)).all()
    all_applications = {}
    for application in all_data:
        if application.company.company_name in all_applications:
            all_applications[application.company.company_name] += 1
        else:
            all_applications[application.company.company_name] = 1
    return all_applications

@my_companies.route('/view_companies', methods=['GET'])
def view_companies():
    all_data = Company.query.all()
    all_applications = countAppsPerCompany() 

    form = CompanyForm()

    return render_template('view_companies.html', title='View Companies', files=all_data, applications=all_applications, form=form)

def check_if_company_exists(name):
    return Company.query.filter(or_(Company.company_name == name)).first() is not None

@my_companies.route('/add_company', methods=['POST','GET'])
def add_company():
    form = CompanyForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_company = Company(
                company_name = form.name.data,
                website = form.url.data,
                careers_page = form.career_page_url.data,
                about = form.description.data,
                types = form.types.data,
                industry = "",
                date_added = datetime.now().strftime('%Y-%m-%d'),
                date_updated = datetime.now().strftime('%Y-%m-%d'),
                deleted = False
            )

            if check_if_company_exists(new_company.company_name):
                flash("Company already exists! Please edit instead.")
            else:    
                db.session.add(new_company)
                db.session.commit()

                return redirect(url_for('my_companies.view_companies'))

    typesT = {}
    listofstates = []
    listofcities = []

    return render_template('add_company.html', title='Add Company', form=form, types=typesT, states=listofstates, cities=listofcities)

@my_companies.route('/edit_company', methods=['POST','GET'])
def edit_company():
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            pass
        return redirect(url_for('view_companies'))
    else:
        form = CompanyForm()

    return render_template('edit_company.html', title='Edit Company')

@my_companies.route('/delete_company', methods=['POST','GET'])
def delete_company():
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            pass
        return redirect(url_for('view_companies'))
    else:
        form = CompanyForm()
    
    return render_template('delete_company.html', title='Delete Company')
