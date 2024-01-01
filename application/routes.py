from application import app, db_mongo_job, db_mongo_food, db_mongo_company, bucket, my_bucket_name, my_bucket_region
from flask import render_template, request, redirect, flash, make_response, jsonify, send_from_directory
from .forms import CompanyForm, FoodForm, ApplicationForm
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid



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

    return render_template('dashboard.html', title='Home', overview=overView)

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
    return render_template('add_company.html', title='Add Company', form=form)

@app.route('/view_companies', methods=['GET', 'POST'])
def view_companies():
    """
    View all companies in the database
    """
    all_data = db_mongo_company.company_list.find()
    return render_template('view_companies.html', title='View Companies', files=all_data)

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
    return render_template('add_application.html', title='Add Application', form=form)

@app.route('/view_applications')
def view_applications():
    """
    View all applications in the database
    """
    all_data = [doc.update({'date': doc['date'].strftime("%B %d, %Y")}) or doc for doc in db_mongo_job.application.find()]
    
    return render_template('view_applications.html', title='View Applications', files=all_data)

@app.route('/edit_application/<id>', methods=['GET', 'POST'])
def edit_application(id):
    """
    Edit an application in the database
    """
    if request.method == 'POST':
        form = ApplicationForm(request.form)
        if form.validate_on_submit():
            name=form.company.data
            position=form.position.data
            date=form.date.data
            date = datetime.combine(date, datetime.min.time())
            link=form.link.data
            email_given=form.email_given.data
            status=form.status.data
            portal=form.portal.data
            notes=form.notes.data

            db_mongo_job.application.update_one(
                {
                    '_id': id
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
    return render_template('edit_application.html', title='Edit Application', form=form)



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
