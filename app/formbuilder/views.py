from flask import (Flask, request, Response, render_template,
        redirect, url_for)

from . import builder
from .. import mongo
from formbuilder import formLoader
import json


mysession = {}
@builder.route('/')
def formbuilder():
    return render_template('formbuilder/formbuilder.html')

@builder.route('/save', methods=['POST'])
def save():
    if request.method == 'POST':
        formData = request.form.get('formData')

        if formData == 'None':
            return 'Error processing request'

        mysession['form_data'] = formData
        formDict = json.loads(formData)
        mongo.db.form.insert_one(formDict)
        return 'OK'

# this url should be checked if have more user.
@builder.route('/render')
def render():
    if not mysession.get('form_data'):
        return redirect('/')

    form_data = mysession.get('form_data')
    mysession['form_data'] = None

    form_loader = formLoader(form_data, url_for('builder.submit'))
    render_form = form_loader.render_form()

    return render_template('formbuilder/render.html', render_form=render_form)

@builder.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        print request.form
        form = json.dumps(request.form)

        return form
