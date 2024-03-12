from flask import Blueprint, render_template

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/', methods=['GET'])
def index():
    overView = {}
    keyword_freq = {}
    img = {}
    return render_template('dashboard.html', title='Home', overview=overView, keyword_freq=keyword_freq, img=img)


@dashboard.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title='About')

@dashboard.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html', title='Settings')

