from application import app, db_mongo_job, db_mongo_food, db_mongo_company, db_mongo_keywords, db_mongo_weight, bucket, my_bucket_name, my_bucket_region, extractor, pdf_extractor, con
from flask import render_template, request, redirect, flash, make_response, jsonify, send_from_directory, url_for, get_flashed_messages
from .forms import CompanyForm, FoodForm, ApplicationForm, LoginForm, WeightTrackerForm
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import json
from .queries import create_tables, insert_dummy
from .utils import JobDescUtils
import base64

descUtils = JobDescUtils()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Check if the file is allowed to be uploaded
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Home page
    """
    # get total number of applications
    num_applications = db_mongo_job.application.count_documents({})

    # get total number of companies
    num_companies = db_mongo_company.company_list.count_documents({})

    # get total number of food
    num_food = db_mongo_food.food_list.count_documents({})

    overView = {
        'Applications I have done': num_applications,
        'Companies in my Database': num_companies,
        'Total food reviews': num_food
    }
    # get notes
    notes = [doc['notes'] for doc in db_mongo_job.application.find()]

    keywords = descUtils.extract_keywords(notes)
    keyword_freq = descUtils.get_keyword_freq(keywords)

    img = descUtils.plot_keyword_freq(keyword_freq, 15)

    # image is in bytes
    # convert to base64
    img = base64.b64encode(img.getvalue()).decode('utf-8')

    """
    To add "location" in all companies
    # db_mongo_company.company_list.update_many({}, {'$set': {'location': None}})
    """

    # create backup of company_list
    # companies = db_mongo_company.company_list.find()
    # for company in companies:
    #     db_mongo_company.company_list_backup.insert_one(company)
    
    # check if all companies have location -> city, state, country if not add it
    # companies = db_mongo_company.company_list.find()
    # for company in companies:
    #     if company['location'] is None:
    #         db_mongo_company.company_list.update_one(
    #             {
    #                 'name': company['name']
    #             },
    #             {
    #                 '$set': {
    #                     'location': {
    #                         'city': company['city'],
    #                         'state': company['state'],
    #                         'country': company['country']
    #                     }
    #                 }
    #             }
    #         )
    #         print(f'Added location for {company["name"]}')

    # remove city, state, country from company
    # db_mongo_company.company_list.update_many({}, {'$unset': {'city': "", 'state': "", 'country': ""}})

    # if location does not exist add it (removed all locations which had values as well. Will have to add city, state, country again)
    # companies = db_mongo_company.company_list.find()
    # for company in companies:
    #     for key in company:
    #         print(key)
    #         if key == 'location':
    #             pass
    #         else:
    #             db_mongo_company.company_list.update_one(
    #                 {
    #                     'name': company['name']
    #                 },
    #                 {
    #                     '$set': {
    #                         'location': {
    #                             'city': None,
    #                             'state': None,
    #                             'country': None
    #                         }
    #                     }
    #                 }
    #             )
    #             print(f'Added location for {company["name"]}')

    # if company_id does not exist add it
    # companies = db_mongo_company.company_list.find()
    # for company in companies:
    #     if 'company_id' not in company:
    #         db_mongo_company.company_list.update_one(
    #             {
    #                 'name': company['name']
    #             },
    #             {
    #                 '$set': {
    #                     'company_id': 0
    #                 }
    #             }
    #         )
    #         print(f'Added company_id for {company["name"]}')

    # if application_id does not exist add it
    # applications = db_mongo_job.application.find()
    # for application in applications:
    #     if 'application_id' not in application:
    #         db_mongo_job.application.update_one(
    #             {
    #                 'name': application['name'],
    #                 'position': application['position']
    #             },
    #             {
    #                 '$set': {
    #                     'application_id': 0
    #                 }
    #             }
    #         )
    #         print(f'Added application_id for {application["name"]}')

    # update application_id starting from 0
    # application_id_start = 1
    # applications = db_mongo_job.application.find()
    # for application in applications:
    #     db_mongo_job.application.update_one(
    #         {
    #             'name': application['name'],
    #             'position': application['position']
    #         },
    #         {
    #             '$set': {
    #                 'application_id': application_id_start
    #             }
    #         }
    #     )
    #     application_id_start += 1
    #     print(f'Updated application_id for {application["name"]}')
    

    # update company_id starting from 0
    # company_id_start = 1
    # companies = db_mongo_company.company_list.find()
    # for company in companies:
    #     db_mongo_company.company_list.update_one(
    #         {
    #             'name': company['name']
    #         },
    #         {
    #             '$set': {
    #                 'company_id': company_id_start
    #             }
    #         }
    #     )
    #     company_id_start += 1
    #     print(f'Updated company_id for {company["name"]}')

    # revert comapny_list to company_list_backup
    # db_mongo_company.company_list.drop()
    # companies = db_mongo_company.company_list_backup.find()
    # for company in companies:
    #     db_mongo_company.company_list.insert_one(company)

    # if 'dateUpdated' does not exist add it
    # companies = db_mongo_company.company_list.find()
    # for company in companies:
    #     if 'dateUpdated' not in company:
    #         db_mongo_company.company_list.update_one(
    #             {
    #                 'name': company['name']
    #             },
    #             {
    #                 '$set': {
    #                     'dateUpdated': company['dateAdded']
    #                 }
    #             }
    #         )
    #         print(f'Added dateUpdated for {company["name"]}')

    app_table, company_table, location_table = create_tables()
    insert_loc, insert_comp, insert_app = insert_dummy()

    # create tables if not exist
    if con:
        with con.cursor() as cur:
            cur.execute(location_table)
            cur.execute(company_table)
            cur.execute(app_table)

            # check if data exists in tables
            cur.execute("SELECT * FROM locations")
            if cur.fetchone() is None:
                cur.execute(insert_loc)
                cur.execute(insert_comp)
                cur.execute(insert_app)
            
            con.commit()
            cur.close()


    # get all keywords
    concepts = db_mongo_keywords.kw.find()

    return render_template('dashboard.html', title='Home', overview=overView, keyword_freq=keyword_freq, img=img, json_data=concepts)

@app.route('/register')
def register():
    """
    Register page
    """
    return render_template('register.html', title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page
    """
    if request.method == 'POST':
        form = LoginForm(request.form)
        if form.validate_on_submit():
            username =form.username.data
            password =form.password.data

            app.logger.info(f'Username: {username} Password: {password}')
            
            # if username == "root" and password == "root":
            return redirect('/')
            # else:
            #     return redirect('/login', form=form)
    else:
        form = LoginForm()

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    return redirect('/login')

@app.route('/forgot')
def forgot():
    """
    Forgot page
    """
    return render_template('forgotpassword.html', title='Forgot')


@app.route('/about')
def about():
    """
    About page
    """
    return render_template('about.html', title='About')


@app.route('/settings')
def settings():
    """
    Settings page
    """
    return render_template('settings.html', title='Settings')

# related to job applications
@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    """
    Add a new company to the database
    """
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            name=form.name.data
            url=form.url.data
            career_page_url=form.career_page_url.data
            description=form.description.data
            types=form.types.data
            city=form.city.data
            state=form.state.data
            country=form.country.data

            location = {}

            if city:
                location['city'] = city
            if state:
                location['state'] = state
            if country:
                location['country'] = country

            try:
                company_id = db_mongo_company.company_list.find_one(
                        sort=[("company_id", -1)]
                    )['company_id'] + 1
            except:
                company_id = 0

            db_mongo_company.company_list.insert_one(
                {
                    'name': name, 
                    'url': url, 
                    'career_page_url': career_page_url, 
                    'description': description, 
                    'types': types, 
                    'location': location,
                    'company_id': company_id,
                    'deleted': False,
                    'dateAdded': datetime.utcnow(),
                    'dateUpdated': datetime.utcnow()
                }
            )
            
            # flash message is displayed on the next page (index)
            flash(f'Company {form.name.data} added!', 'success')

            return redirect('/add_company')
    else:
        form = CompanyForm()

    # get all company types
    # companies = db_mongo_company.company_types.find()
    # types = json.dumps([company['types'] for company in companies], default=str)

    listofstates, listofcities = getStatesAndCities()
    typesT = getTypesOfCompanies()

    return render_template('add_company.html', title='Add Company', form=form, types=typesT, states=listofstates, cities=listofcities)

def countAppsPerCompany():
    """
    Count number of applications per company
    """
    total_applications = {}

    # get all companies
    companies = db_mongo_company.company_list.find()

    for company in companies:
        name = company['name']
        total_applications[name] = db_mongo_job.application.count_documents({'name': name})

    return total_applications

@app.route('/view_companies', methods=['GET', 'POST'])
def view_companies():
    """
    View all companies in the database
    """
    all_data = db_mongo_company.company_list.find()
    applications = countAppsPerCompany()
    form = CompanyForm(request.form)


    return render_template('view_companies.html', title='View Companies', files=all_data, applications=applications, form=form)

@app.route('/edit_company/<name>', methods=['GET', 'POST'])
def edit_company(name):
    """
    Edit a company in the database
    """
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            name=form.name.data
            url=form.url.data
            career_page_url=form.career_page_url.data
            description=form.description.data
            types=form.types.data
            city=form.city.data
            state=form.state.data
            country=form.country.data

            location = {}

            if city:
                location['city'] = city
            else:
                location['city'] = None

            if state:
                location['state'] = state
            else:
                location['state'] = None

            if country:
                location['country'] = country
            else:
                location['country'] = None           

            db_mongo_company.company_list.update_one(
                {
                    'name': name
                },
                {
                    '$set': {
                        'name': name, 
                        'url': url, 
                        'career_page_url': career_page_url, 
                        'description': description, 
                        'types': types,
                        'location': location,
                        'dateUpdated': datetime.utcnow()
                    }
                }
            )
            
            # flash message is displayed on the next page (index)
            flash(f'Company {form.name.data} added!', 'success')

            return redirect(url_for('view_companies'))
    else:
        form = CompanyForm()
        # set form values
        company = db_mongo_company.company_list.find_one({'name': name})

        form.name.data = company['name']
        form.url.data = company['url']
        form.career_page_url.data = company['career_page_url']
        form.description.data = company['description']
        form.types.data = company['types']

        form.city.data = company['location']['city']
        form.state.data = company['location']['state']
        form.country.data = company['location']['country']

    typesT = getTypesOfCompanies()

    listofstates, listofcities = getStatesAndCities()
    
    return render_template('edit_company.html', title='Edit Company', form=form, states=listofstates, cities=listofcities, types=typesT)

def getStatesAndCities():
    """
    Get all states and cities
    """
    listofstates = []
    listofcities = []

    # get all states
    locations = db_mongo_company.company_list.find({}, {'location': 1, '_id': 0})
    for location in locations:
        if location['location']['state'] not in listofstates and location['location']['state'] is not None:
            listofstates.append(location['location']['state'])
        if location['location']['city'] not in listofcities and location['location']['city'] is not None:
            listofcities.append(location['location']['city'])

    listofstates = json.dumps(listofstates, default=str)
    listofcities = json.dumps(listofcities, default=str)

    return listofstates, listofcities


def getTypesOfCompanies():
    """
    Get all types of companies
    """
    listOfTypes = []
    companies = db_mongo_company.company_types.find()
    for company in companies:
        listOfTypes.append(company['types'])
    typesT = json.dumps(listOfTypes, default=str)

    return typesT


@app.route('/delete_company/<name>', methods=['GET', 'POST'])
def delete_company(name):
    """
    Delete a company in the database
    """
    # updated "deleted" field to true
    db_mongo_company.company_list.update_one(
        {
            'name': name
        },
        {
            '$set': {
                'deleted': True
            }
        }
    )
    return redirect('/view_companies')

@app.route('/edit_application/<name>/<position>', methods=['GET', 'POST'])
def edit_application(name, position):
    """
    Edit an application in the database
    """
    if request.method == 'POST':
        form = ApplicationForm(request.form)
        if form.validate_on_submit():
            name=form.company.data
            position=form.position.data
            date=form.date.data
            date = datetime.strptime(str(date), '%Y-%m-%d')
            link=form.link.data
            email_given=form.email_given.data
            status=form.status.data
            portal=form.portal.data
            notes=form.notes.data

            db_mongo_job.application.update_one(
                {
                    'name': name,
                    'position': position
                },
                {
                    '$set': {
                        'name': name, 
                        'position': position,
                        'date': date,
                        'link': link,
                        'email_given': email_given,
                        'status': status,
                        'portal': portal,
                        'notes': notes,
                    }
                }
            )
            
            # flash message is displayed on the next page (index)
            flash(f'Company {form.company.data} added!', 'success')

            return redirect('/view_applications')
    else:
        form = ApplicationForm()

        name = name.replace("%20", " ")
        position = position.replace("%20", " ")        

        application = db_mongo_job.application.find_one({'name': name, 'position': position})
        form.company.data = application['name']
        form.position.data = application['position']
        form.date.data = application['date']
        form.link.data = application['link']
        form.email_given.data = application['email_given']
        form.status.data = application['status']
        form.portal.data = application['portal']
        form.notes.data = application['notes']

    companies = db_mongo_company.company_list.find()
    companies = json.dumps([company['name'] for company in companies], default=str)

    return render_template('edit_application.html', title='Edit Application', form=form, companies=companies)

@app.route('/delete_application/<name>/<position>', methods=['GET', 'POST'])
def delete_application(name, position):
    """
    Delete an application in the database
    """
    # updated "deleted" field to true
    db_mongo_job.application.update_one(
        {
            'name': name,
            'position': position
        },
        {
            '$set': {
                'deleted': True
            }
        }
    )
    return redirect('/view_applications')
    

@app.route('/add_application', methods=['GET', 'POST'])
def add_application():
    """
    Add a new application to the database
    """
    if request.method == 'POST':
        form = ApplicationForm(request.form)
        if form.validate_on_submit():
            name=form.company.data
            position=form.position.data

            # if position contains / replace with -
            if "/" in position:
                position = position.replace("/", "-")

            date=form.date.data
            date = datetime.strptime(str(date), '%Y-%m-%d')
            link=form.link.data
            email_given=form.email_given.data
            status=form.status.data
            portal=form.portal.data
            notes=form.notes.data
            deleted=False

            extracted_keywords = extractor.extract_keywords(notes)
            
            try:
                application_id = db_mongo_job.application.find_one(
                        sort=[("application_id", -1)]
                    )['application_id'] + 1
            except:
                application_id = 0
            
            try:
                company_id = db_mongo_company.company_list.find_one(
                        sort=[("company_id", -1)]
                    )['company_id'] + 1
            except:
                company_id = 0

            add_company_if_id_does_not_exist(company_id, name)

            db_mongo_job.application.insert_one(
                {
                    'name': name, 
                    'position': position,
                    'date': date,
                    'link': link,
                    'email_given': email_given,
                    'status': status,
                    'portal': portal,
                    'notes': notes,
                    'deleted': deleted,
                    'application_id': application_id
                }
            )
            
            # flash message is displayed on the next page (index)
            flash(f'Company {form.company.data} added!', 'success')

            return redirect('/add_application')
    else:
        form = ApplicationForm()

    # get all companies
    companies = db_mongo_company.company_list.find()

    # get company names
    companies = json.dumps([company['name'] for company in companies], default=str)

    return render_template('add_application.html', title='Add Application', form=form, companies=companies)


def add_company_if_id_does_not_exist(id, name):
    default_company_doc = {
        'url': None,
        'career_page_url': None,
        'description': None,
        'types': None,
        'location': {
            'city': None,
            'state': None,
            'country': None
        },
        'deleted': False,
        'dateAdded': datetime.utcnow(),
        'dateUpdated': datetime.utcnow()
    }

    db_mongo_company.company_list.update_one(
        {'name': name},
        {'$setOnInsert': {
            'name': name,
            'company_id': id,
            **default_company_doc
        }},
        upsert=True
    )


@app.route('/view_applications')
def view_applications():
    """
    View all applications in the database
    """
    all_data = [doc.update({'date': doc['date'].strftime("%m/%d/%Y")}) or doc for doc in db_mongo_job.application.find()]
    
    return render_template('view_applications.html', title='View Applications', files=all_data)

@app.route('/view_applications/<name>')
def view_applications_by_company(name):
    """
    View all applications in the database by company
    """
    all_data = [doc.update({'date': doc['date'].strftime("%B %d, %Y")}) or doc for doc in db_mongo_job.application.find()]

    return render_template('view_applications.html', title='View Applications', files=all_data, name=name)

# related to food I tried
@app.route('/add_new_food', methods=['GET', 'POST'])
def add_new_food():
    """
    Add a new food to the database
    """
    if request.method == 'POST':
        form = FoodForm(request.form)
        name=form.name.data
        description=form.description.data
        price=form.price.data
        brand=form.brand.data
        category=form.category.data
        city=form.city.data
        state=form.state.data
        country=form.country.data
        image_data = request.files['file-to-upload']

        if image_data:
            new_filename = secure_filename(image_data.filename)
            new_filename = str(uuid.uuid4().hex) + "." + new_filename.rsplit('.', 1)[1].lower()
        else:
            new_filename = None
        
        if image_data and allowed_file(image_data.filename):
            bucket.upload_fileobj(image_data, new_filename, ExtraArgs={'ACL': 'public-read'})
        else:
            image_data = None

        db_mongo_food.food_list.insert_one(
            {
                'name': name, 
                'description': description, 
                'price': price, 
                'brand': brand, 
                'category': category, 
                'city': city, 
                'state': state, 
                'country': country,
                'image_data': new_filename,
                'dateAdded': datetime.utcnow()
            }
        )
        
        # flash message is displayed on the next page (index)
        flash(f'Food {form.name.data} added!', 'success')

        return redirect('/view_food')
    else:
        form = FoodForm()

    return render_template('add_new_food.html', title='Add Food', form=form)

@app.route('/view_food')
def view_food():
    """
    View all food in the database
    """
    all_data = db_mongo_food.food_list.find()
    return render_template('view_food.html', title='View Food', files=all_data, bucket=my_bucket_name, region=my_bucket_region)

@app.errorhandler(413)
def too_large(e):
    """
    Error handler for file too large
    """
    return make_response(jsonify(message="File is too large"), 413)

# get flashed messages
@app.route('/get_flashed_messages')
def get_flashed_messages():
    """
    Get flashed messages
    """
    messages = []
    for message in get_flashed_messages():
        messages.append(message)
    return jsonify(messages)

@app.errorhandler(404)
def page_not_found(e):
    """
    Error handler for page not found
    """
    return render_template('404.html', title='404'), 404

@app.route('/log_weight', methods=['GET', 'POST'])
def log_weight():
    """
    Log weight
    """
    if request.method == 'POST':
        form = WeightTrackerForm(request.form)
        if form.validate_on_submit():
            weight = form.weight.data
            date = form.date.data

            # convert date to datetime
            date = datetime.strptime(str(date), '%Y-%m-%d')

            db_mongo_weight.weight_tracker.insert_one(
                {
                    'weight': weight,
                    'date': date
                }
            )

            flash(f'Weight {form.weight.data} added!', 'success')

            return redirect('/log_weight')
    else:
        form = WeightTrackerForm()
        
        # get all weight data
        weight_data = db_mongo_weight.weight_tracker.find()

    return render_template('weight_tracker.html', title='Log Weight', form=form, weight_data=weight_data)