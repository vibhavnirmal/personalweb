from application import app, db_mongo_job, db_mongo_food, bucket, my_bucket_name, my_bucket_region
from flask import render_template, request, redirect, flash, make_response, jsonify, send_from_directory
from .forms import CompanyForm, FoodForm, ApplicationForm
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('dashboard.html', title='Home')


# related to job applications
@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        form = CompanyForm(request.form)
        if form.validate_on_submit():
            name=form.name.data
            url=form.url.data
            careerPageUrl=form.careerPageUrl.data
            description=form.description.data
            types=form.types.data
            city=form.city.data
            state=form.state.data
            country=form.country.data

            db_mongo_job.company_list.insert_one(
                {
                    'name': name, 
                    'url': url, 
                    'careerPageUrl': careerPageUrl, 
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

            return redirect('/')
    else:
        form = CompanyForm()
    return render_template('add_company.html', title='Add Company', form=form)

@app.route('/view_companies', methods=['GET', 'POST'])
def view_companies():
    all_data = db_mongo_job.company_list.find()
    return render_template('view_companies.html', title='View Companies', files=all_data)

@app.route('/add_application', methods=['GET', 'POST'])
def add_application():
    if request.method == 'POST':
        form = ApplicationForm(request.form)
        if form.validate_on_submit():
            name=form.name.data
            url=form.url.data
            careerPageUrl=form.careerPageUrl.data
            description=form.description.data
            types=form.types.data
            city=form.city.data
            state=form.state.data
            country=form.country.data

            db_mongo_job.company_list.insert_one(
                {
                    'name': name, 
                    'url': url, 
                    'careerPageUrl': careerPageUrl, 
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

            return redirect('/')
    else:
        form = ApplicationForm()
    return render_template('add_application.html', title='Add Application', form=form)

@app.route('/view_applications')
def view_applications():
    return render_template('view_applications.html', title='View Applications')


# related to food I tried
@app.route('/add_new_food', methods=['GET', 'POST'])
def add_new_food():
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

        return redirect('/')
    else:
        form = FoodForm()

    return render_template('add_new_food.html', title='Add Food', form=form)

@app.route('/view_food')
def view_food():
    all_data = db_mongo_food.food_list.find()
    return render_template('view_food.html', title='View Food', files=all_data, bucket=my_bucket_name, region=my_bucket_region)

@app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)