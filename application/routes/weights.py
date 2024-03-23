from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..forms import WeightTrackerForm

from ..models.weights import Weights
from ..extensions import db

from datetime import datetime

my_weight_tracking = Blueprint('my_weight_tracking', __name__, url_prefix='/weight_tracking')

@my_weight_tracking.route('/', methods=['POST','GET'])
def log_weight():
    if request.method == 'POST':
        form = WeightTrackerForm(request.form)
        if form.validate_on_submit():
            new_weights = Weights(
                weight = form.weight.data,
                date_added = datetime.strptime(str(form.date_added.data), '%Y-%m-%d')
            )

            db.session.add(new_weights)
            db.session.commit()

        return redirect(url_for('my_weight_tracking.log_weight'))
    else:
        form = WeightTrackerForm()

        all_data = Weights.query.all()
        for weight in all_data:
            weight.date_added = weight.date_added.strftime("%Y-%m-%d")
        
        # sort by date_added 
        all_data = sorted(all_data, key=lambda x: x.date_added)

    return render_template('weight/weight_tracker.html', title='Log Weight', form=form, weight_data=all_data)