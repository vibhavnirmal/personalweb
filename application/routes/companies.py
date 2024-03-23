from re import A
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import json

from ..extensions import db

from ..models.applications import Application
from ..models.companies import Company
from ..models.keywords import Keyword, KeywordAssociation

from ..forms import CompanyForm
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, or_

from datetime import datetime

my_companies = Blueprint('my_companies', __name__, url_prefix='/companies')

def count_apps_per_company():
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

    all_applications = count_apps_per_company() 

    form = CompanyForm()

    return render_template('company/view_companies.html', title='View Companies', files=all_data, applications=all_applications, form=form)

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

                logo = form.logo.data,
                linkedin = form.linkedin.data,

                location = json.dumps({
                    "city": form.city.data,
                    "state": form.state.data,
                    "country": form.country.data
                    }),

                date_added = datetime.now().date(),
                date_updated = datetime.now().date(),
                deleted = False
            )

            if check_if_company_exists(new_company.company_name):
                flash("Company already exists! Please edit instead.")
            else:    
                db.session.add(new_company)
                db.session.commit()

                return redirect(url_for('my_companies.view_companies'))

    typesT = get_types_of_companies()
    listofstates = []
    listofcities = []

    return render_template('company/add_company.html', title='Add Company', form=form, types=typesT, states=listofstates, cities=listofcities)

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

            company.logo = form.logo.data
            company.linkedin = form.linkedin.data

            company.location = json.dumps({
                "city": form.city.data,
                "state": form.state.data,
                "country": form.country.data
            })

            company.date_updated = datetime.now().date()
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

        form.logo.data = company.logo
        form.linkedin.data = company.linkedin

        locations = json.loads(company.location) if company.location else {}

        form.city.data = locations.get('city', 'NA')
        form.state.data = locations.get('state', 'NA')
        form.country.data = locations.get('country', 'NA')
        
    typesT = get_types_of_companies()

    return render_template('company/edit_company.html', title='Edit Company', form=form, types=typesT, locs = locations)

@my_companies.route('/delete_company', methods=['POST','GET'])
def delete_company():
    company_id = request.args.get('id')

    company = Company.query.filter_by(id=company_id).first()

    company.deleted = True
    company.date_updated = datetime.now().date()

    db.session.commit()

    return redirect(url_for('my_companies.view_companies'))

def get_types_of_companies():
    companyTypes = set()
    for company in Company.query.all():
        companyTypes.add(company.types)
    companyTypes = json.dumps(companyTypes, default=str)
    return companyTypes

def preprocessDescription(description):
    description = description.replace("\n", " ")
    description = description.replace("\r", " ")
    description = description.replace("\t", " ")
    description = description.replace("  ", " ")
    return description

def get_keywords(application_ids):
    keywords = KeywordAssociation.query.filter(KeywordAssociation.application_id.in_(application_ids)).all()
    keywords = [keyword.keyword for keyword in keywords]
    return keywords

@my_companies.route('/<company_name>')
def view_company(company_name):
    # Fetch the company by its name
    company = Company.query.filter_by(company_name=company_name).first_or_404()

    # Parse location JSON
    if company.location is not None:
        location_data = json.loads(company.location)
        city = location_data.get('city')
        state = location_data.get('state')
        country = location_data.get('country')
        location = f"{city} · {state} · {country}" if city and state and country else "Not Available"
    else:
        location = "Not Available"
    
    # Fetch all applications associated with the company
    applications = Application.query.filter_by(company_id=company.id).all()
    application_ids = [app.id for app in applications]

    # Preprocess descriptions
    for application in applications:
        application.description = preprocessDescription(application.description)
        
    # Fetch keywords for all applications
    kws = get_keywords(application_ids)

    # Pass the company and its applications to the template
    return render_template('company/view_company.html', company=company, applications=applications, loc=location, kws=kws)