#!/usr/bin/env python
# -*- coding : utf-8 -*-

import os
from app import create_app, mongo
from flask_script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

#print app.url_map

manager = Manager(app)
def make_shell_context():
    return dict(app=app, mongo=mongo)
manager.add_command('shell', Shell(make_context=make_shell_context, use_ipython=True))
    


if __name__ == '__main__':
    manager.run()
