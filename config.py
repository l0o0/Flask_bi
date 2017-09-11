# -*- coding: utf-8 -*-

import os


class Config:
    
    SECRET_KEY = os.getenv('SECRET_KEY','NOTSECURELOL')

    MONGO_URI='mongodb://localhost:27017/formtable'
    MONGO_USERNAME='flask'
    MONGO_PASSWORD='flask@1gene'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    # jsondash config
    JSONDASH_FILTERUSERS=False
    JSONDASH_GLOBALDASH=True
    JSONDASH_GLOBAL_USER='global'

    def _can_edit_global():
        return True

    def _can_delete():
        return True

    def _can_clone():
        return True

    def _get_username():
        return 'anonymous'

    JSONDASH = dict(
            metadata=dict(
                created_by=_get_username,
                username=_get_username,
                ),
            static=dict(
                js_path='js/vendor/',
                css_path='css/vendor/',
                ),
            auth=dict(
                edit_global=_can_edit_global,
                clone=_can_clone,
                delete=_can_delete,
                )
            )


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
