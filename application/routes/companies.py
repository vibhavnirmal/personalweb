from flask import Blueprint, render_template, request, redirect, url_for, flash
import json

from ..extensions import db

from ..models.applications import Application
from ..models.companies import Company

from ..forms import CompanyForm
from sqlalchemy.orm import joinedload
from sqlalchemy import or_

from datetime import datetime

from application.models import locations

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

    for company in all_data:
        company.date_added = company.date_added.strftime("%m/%d/%Y")
        company.date_updated = company.date_updated.strftime("%m/%d/%Y")
        if company.location is not None:
            company.location = json.loads(company.location).get('city')

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

                location = json.dumps({
                    "city": form.city.data,
                    "state": form.state.data,
                    "country": form.country.data
                    }),

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

    typesT = getTypesOfCompanies()
    listofstates = []
    listofcities = []

    return render_template('add_company.html', title='Add Company', form=form, types=typesT, states=listofstates, cities=listofcities)

@my_companies.route('/edit_company', methods=['POST','GET'])
def edit_company():
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            company_id = request.args.get('id')

            company = Company.query.filter_by(id=company_id).first()

            company.company_name = form.name.data
            company.website = form.url.data
            company.careers_page = form.career_page_url.data
            company.about = form.description.data
            company.types = form.types.data

            company.location = json.dumps({
                "city": form.city.data,
                "state": form.state.data,
                "country": form.country.data
            })

            company.date_updated = datetime.now().strftime('%Y-%m-%d')
            company.deleted = False

            db.session.commit()

        return redirect(url_for('my_companies.view_companies'))
    else:
        form = CompanyForm()

        company_id = request.args.get('id')

        company = Company.query.filter_by(id=company_id).first()

        form.name.data = company.company_name
        form.url.data = company.website
        form.career_page_url.data = company.careers_page
        form.description.data = company.about
        form.types.data = company.types

        locations = company.location
        if locations is not None and 'city' in locations:
            form.city.data = locations['city']
            form.state.data = locations['state']
            form.country.data = locations['country']
        else:
            form.city.data = "NA"
            form.state.data = "NA"
            form.country.data = "NA"
        
    typesT = getTypesOfCompanies()

    return render_template('edit_company.html', title='Edit Company', form=form, types=typesT, locs = locations)

@my_companies.route('/delete_company', methods=['POST','GET'])
def delete_company():
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            pass
        return redirect(url_for('view_companies'))
    else:
        form = CompanyForm()
    
    return render_template('delete_company.html', title='Delete Company', form=form)


def getTypesOfCompanies():
    companyTypes = set()
    for company in Company.query.all():
        companyTypes.add(company.types)
    companyTypes = json.dumps(companyTypes, default=str)
    return companyTypes
