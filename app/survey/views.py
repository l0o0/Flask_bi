# -*- coding:utf-8 -*-
import time
from base64 import urlsafe_b64decode as url_decode
from bson.json_util import loads, dumps
from flask import (request, url_for, render_template, redirect, flash,
                abort)
from flask_login import login_required, current_user
from . import survey
from .. import mongo
from ..formbuilder.formbuilder import formLoader



# Show the survey table.
@survey.route('/<url_hash>', methods=['GET', 'POST'])
@login_required
def survey_user(url_hash):
    form_data = dumps(mongo.db.formtable.find_one({'url_hash' : url_hash }))
    form_loader = formLoader(form_data, url_for('survey.submit', url_hash=url_hash))
    render_form = form_loader.render_form()
    return render_template('formbuilder/render.html', render_form=render_form)



# Show the survey table for public.    
@survey.route('/public/<url_hash>', methods=['POST','GET'])
def survey_publish(url_hash):
    formData = mongo.db.formtable.find_one({'url_hash':url_hash})
    if not formData.get('public'):
        abort(403)
    form_loader = formLoader(dump(formData), url_for('survey.submit', url_hash=url_hash))
    render_form = form_loader.render_form()
    return render_template('formbuilder/render.html', render_form=render_form)


# Submit the survey data to database.    
@survey.route('/submit/<url_hash>', methods=['POST'])
def submit(url_hash):
    if request.method == 'POST':
        form = dumps(request.form)
        form_data = request.form.to_dict()
        form_data['url_hash'] = url_hash
        form_data['submit_version'] = "UnderDevelopment"
        form_data['submit_user'] = current_user.username
        form_data['submit_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mongo.db.demo.insert_one(form_data)
        flash(u'数据已经提交')
        if current_user.username == 'AnonymousUser':
            return redirect(url_for('survey.survey_publish', url_hash=url_hash))
        else:
            return redirect(url_for('survey.survey_user', url_hash = url_hash))
            