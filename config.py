# -*- coding: utf-8 -*-

import os


class Config:
    MONGO_URI='mongodb://localhost:27017/formtable'
    MONGO_USERNAME='flask'
    MONGO_PASSWORD='flask@1gene'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    @staticmethod
    def init_app(app):
        pass



class DevelopmentConfig(Config):
    DEBUG=True
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
