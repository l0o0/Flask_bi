# -*- coding: utf-8 -*-

import os


class Config:
    
    SECRET_KEY = os.getenv('SECRET_KEY','NOTSECURELOL')

    MONGO_URI='mongodb://localhost:27017/formtable'
    MONGO_USERNAME='flask'
    MONGO_PASSWORD='flask@1gene'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    PAGESIZE = 20
    FLASK_ADMIN = 'linxingzhong@1gene.com.cn'
    
   



    @staticmethod
    def init_app(app):
        pass



class DevelopmentConfig(Config):
    DEBUG=True
    MONGO_URI='mongodb://localhost:27017/test'
    pass


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    pass


Configure = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig
}
