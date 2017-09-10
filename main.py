#!/usr/bin/env python
# -*- coding : utf-8 -*-

import os
from app import create_app
from flask_script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

app.config['SECRET_KEY'] = 'NOTSECURELOL'
app.config.update(
    JSONDASH_FILTERUSERS=False,
    JSONDASH_GLOBALDASH=True,
    JSONDASH_GLOBAL_USER='global',
)


def _can_edit_global():
    return True


def _can_delete():
    return True


def _can_clone():
    return True


def _get_username():
    return 'anonymous'


# Config examples.
app.config['JSONDASH'] = dict(
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

print app.url_map

manager = Manager(app)
def make_shell_context():
    return dict(app=app)
    manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
