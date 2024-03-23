from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..forms import FoodForm

food_track = Blueprint('food_track', __name__, url_prefix='/food_track')

@food_track.route('/add_food_review', methods=['POST','GET'])
def add_new_food():
    if request.method == 'POST':
        form = FoodForm(request.form)
        if form.validate_on_submit():
            pass
        return redirect(url_for('view_food'))
    
    else:
        form = FoodForm()
    
    return render_template('foodreview/add_food_review.html', title='Add Food Review', form=form)

@food_track.route('/view_food', methods=['GET'])
def view_food():
    all_data = []
    return render_template('foodreview/view_food.html', title='View Food', files=all_data)
