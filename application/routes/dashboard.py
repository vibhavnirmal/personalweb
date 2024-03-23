from flask import Blueprint, render_template

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime

from ..models.companies import Company
from ..models.keywords import Keyword
from ..models.applications import Application

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/', methods=['GET'])
def index():
    overView = {}
    keyword_freq = {}
    
    # get total company count
    total_companies = Company.query.count()

    # get total applications count
    total_applications = Application.query.count()

    # get total keywords count
    total_keywords = Keyword.query.count()

    overView['total_companies'] = total_companies
    overView['total_applications'] = total_applications
    overView['total_keywords'] = total_keywords

    # get top 10 keywords
    top_n = 10
    keywords = Keyword.query.order_by(Keyword.frequency.desc()).limit(top_n).all()
    for keyword in keywords:
        keyword_freq[keyword.keyword] = keyword.frequency

    # plot keyword frequency
    img = plot_keyword_freq(keyword_freq)
    # save img in static/images/plots
    # get datetime now
    now = datetime.now()
    with open('application/static/plots/keyword_freq_' + now.strftime("%Y-%m-%d-%H-%M-%S") + '.jpg', 'wb') as f:
        f.write(img.read())
    
    imgPath = '/static/plots/keyword_freq_' + now.strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'
    
    return render_template('dashboard.html', title='Home', overview=overView, keyword_freq=keyword_freq, imgPath=imgPath)

def plot_keyword_freq(keyword_freq):
    plt.figure(figsize=(10, 7))
    plt.bar(range(len(keyword_freq)), list(keyword_freq.values()), align='center')
    plt.xticks(range(len(keyword_freq)), list(keyword_freq.keys()), rotation='vertical')
    plt.title('Keyword Frequency')
    plt.ylabel('Frequency')
    plt.xlabel('Keyword')
    plt.tight_layout()
    plt.grid()

    # return jpeg image to show in html
    buf = io.BytesIO()
    plt.savefig(buf, format='jpeg')
    buf.seek(0)
    plt.close()

    return buf

@dashboard.route('/about', methods=['GET'])
def about():
    return render_template('about.html', title='About')

@dashboard.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html', title='Settings')

