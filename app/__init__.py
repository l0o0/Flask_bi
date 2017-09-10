from flask import Flask
from flask_pymongo import PyMongo
from config import Configure

mongo = PyMongo()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(Configure[config_name])
    Configure[config_name].init_app(app)

    mongo.init_app(app)

    from .formbuilder import builder as builder_blueprint
    app.register_blueprint(builder_blueprint, url_prefix='/formbuilder')
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # register flask jsondash charts, url prefix is charts
    from flask_jsondash.charts_builder import charts
    app.register_blueprint(charts)

    return app
