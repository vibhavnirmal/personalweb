from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..models.keywords import Keyword, KeywordAssociation

from ..extensions import db

my_keywords = Blueprint('my_keywords', __name__, url_prefix='/keywords')

@my_keywords.route('/view_keywords', methods=['GET'])
def view_keywords():
    all_data = Keyword.query.all()
    return render_template('keywords/view_kws.html', title='View Keywords', files=all_data)
