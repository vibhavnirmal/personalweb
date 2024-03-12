from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..forms import WeightTrackerForm

my_weight_tracking = Blueprint('my_weight_tracking', __name__, url_prefix='/weight_tracking')

@my_weight_tracking.route('/', methods=['POST','GET'])
def log_weight():
    if request.method == 'POST':
        form = WeightTrackerForm(request.form)
        if form.validate_on_submit():
            pass
        return redirect(url_for('log_weight'))
    else:
        form = WeightTrackerForm()

    weight_data = []
    return render_template('weight_tracker.html', title='Log Weight', form=form, weight_data=weight_data)