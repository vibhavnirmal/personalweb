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
    return render_template('dashboard.html', title='Home')

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
            # bson.errors.InvalidDocument: cannot encode object: datetime.date(2023, 12, 20), of type: <class 'datetime.date'>
            date = datetime.combine(date, datetime.min.time())
            link=form.link.data
            email_given=form.email_given.data
            status=form.status.data
            portal=form.portal.data
            notes=form.notes.data

            db_mongo_job.company_list.insert_one(
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
    all_data = db_mongo_job.company_list.find()
    return render_template('view_applications.html', title='View Applications', files=all_data)


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

        new_filename = secure_filename(image_data.filename)
        new_filename = str(uuid.uuid4().hex) + "." + new_filename.rsplit('.', 1)[1].lower()
        
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