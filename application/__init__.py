from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from .extensions import db

from .routes.applications import my_applications
from .routes.companies import my_companies
from .routes.dashboard import dashboard
from .routes.weights import my_weight_tracking
from .routes.food import food_track
from .routes.track import my_watchlist
from .routes.keywords import my_keywords

def create_app(config_file='config.py'):
    app = Flask(__name__)
    CORS(app)
    
    app.config.from_pyfile(config_file)

    db.init_app(app)

    migrate = Migrate(app, db, directory='application/migrations')

    app.register_blueprint(my_applications)
    app.register_blueprint(my_companies)
    app.register_blueprint(dashboard)
    app.register_blueprint(my_weight_tracking)
    app.register_blueprint(food_track)
    app.register_blueprint(my_keywords)
    app.register_blueprint(my_watchlist)

    return app