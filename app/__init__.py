# -*- coding:utf-8 -*-
from flask import Flask
from flask_pymongo import PyMongo
from config import Configure
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment

mongo = PyMongo()
bootstrap = Bootstrap()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

mail = Mail()
moment = Moment()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(Configure[config_name])
    Configure[config_name].init_app(app)

    mongo.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    
    # 创建和修改调查问卷的蓝图
    from .formbuilder import builder as builder_blueprint
    app.register_blueprint(builder_blueprint, url_prefix='/form')
    # 主要的页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # 用于登录和注册使用的蓝图
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    # 发布调查问卷，进行数据收集的蓝图
    from .survey import survey as  survey_blueprint
    app.register_blueprint(survey_blueprint, url_prefix='/survey')
    # 查看数据库信息的蓝图
    from .database import database as db_blueprint
    app.register_blueprint(db_blueprint, url_prefix='/db')
    # register flask jsondash charts, url prefix is charts
    from flask_jsondash.charts_builder import charts
    app.register_blueprint(charts)

    return app
