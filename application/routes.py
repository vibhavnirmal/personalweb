from application import app, db_mongo_job, db_mongo_food, db_mongo_company, db_mongo_keywords, bucket, my_bucket_name, my_bucket_region
from flask import render_template, request, redirect, flash, make_response, jsonify, send_from_directory, url_for, get_flashed_messages
from .forms import CompanyForm, FoodForm, ApplicationForm, LoginForm
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
import json
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

            db_mongo_company.company_list.insert_one(
                {
                    'name': name, 
                    'url': url, 
                    'career_page_url': career_page_url, 
                    'description': description, 
                    'types': types, 
                    'city': city, 
                    'state': state, 
                    'country': country, 
                    'dateAdded': datetime.utcnow()
                }
            )
            
            # flash message is displayed on the next page (index)
            flash(f'Company {form.name.data} added!', 'success')

            return redirect('/add_company')
    else:
        form = CompanyForm()

    # get all company types
    companies = db_mongo_company.company_types.find()
    types = json.dumps([company['types'] for company in companies], default=str)


    return render_template('add_company.html', title='Add Company', form=form, types=types)

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
                        'city': city, 
                        'state': state, 
                        'country': country
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
        form.city.data = company['city']
        form.state.data = company['state']
        form.country.data = company['country']

    mutypes = json.dumps([comp['types'] for comp in db_mongo_company.company_types.find()], default=str)

    return render_template('edit_company.html', title='Edit Company', form=form, types=mutypes)

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
                        'notes': notes
                    }
                }
            )
            
            # flash message is displayed on the next page (index)
            flash(f'Company {form.company.data} added!', 'success')

            return redirect('/view_applications')
    else:
        form = ApplicationForm()
        # set form values
        
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

    # get all companies
    companies = db_mongo_company.company_list.find()

    # get company names
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

            # check if company exists if not add it
            if db_mongo_company.company_list.find_one({'name': name}) is None:
                db_mongo_company.company_list.insert_one(
                    {
                        'name': name, 
                        'url': None, 
                        'career_page_url': None, 
                        'description': None, 
                        'types': None, 
                        'city': None, 
                        'state': None, 
                        'country': None, 
                        'dateAdded': datetime.utcnow()
                    }
                )


            db_mongo_job.application.insert_one(
                {
                    'name': name, 
                    'position': position,
                    'date': date,
                    'link': link,
                    'email_given': email_given,
                    'status': status,
                    'portal': portal,
                    'notes': notes
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

@app.route('/view_applications')
def view_applications():
    """
    View all applications in the database
    """
    all_data = [doc.update({'date': doc['date'].strftime("%B %d, %Y")}) or doc for doc in db_mongo_job.application.find()]

    # # get notes
    # notes = [doc['notes'] for doc in db_mongo_job.application.find()]

    # keywords = descUtils.extract_keywords(notes)

    # insights = descUtils.get_insights(keywords)
    
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


# if path is not found
@app.errorhandler(404)
def page_not_found(e):
    """
    Error handler for page not found
    """
    return render_template('404.html', title='404'), 404
