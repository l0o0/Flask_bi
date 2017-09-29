# -*- coding:utf-8 -*-
import time
from bson.json_util import loads, dumps
from bson import ObjectId
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
    '''
    url_hash is the _id of pymongodb object.
    You can test the code below to see what happens.
    
    >>> url_hash = str(query['_id'])
    >>> from bson import ObjectId
    >>> _id = ObjectId(url_hash)
    >>> _id = query['_id']
    True
    
    '''
    # 获得 formlist.html中传递进来的preview参数，
    # 如果是preview的话，那表单的提交是无效的。避免在preview的时候往数据库添加数据
    preview = int(request.args.get('preview', '0'))
    mongoid = ObjectId(url_hash)
    formData = mongo.db.formtable.find_one({'_id' : mongoid })
    
    if not preview:
        print 'no preview'
        form_loader = formLoader(formData, url_for('survey.submit', url_hash=url_hash))
    else:
        print 'preview'
        form_loader = formLoader(formData, url_form('builder.submit_time'))   
    render_form = form_loader.render_form()
    return render_template('formbuilder/render.html', render_form=render_form)



# Show the survey table for public.    
@survey.route('/public/<url_hash>', methods=['POST','GET'])
def survey_publish(url_hash):
    preview = int(request.args.get('preview', '0'))
    mongoid = ObjectId(url_hash)
    formData = mongo.db.formtable.find_one({'_id':mongoid})
    
    # 如果表单是不公开的，没注册用户是没有权限打开的
    if not formData.get('public'):
        abort(403)
    
    if not preview:
        form_loader = formLoader(dumps(formData), url_for('survey.submit', url_hash=url_hash))
    else:
        form_loader = formLoader(dumps(formData), url_form('builder.submit_time'))    
    render_form = form_loader.render_form()
    return render_template('formbuilder/render.html', render_form=render_form)


# Submit the survey data to database.    
@survey.route('/submit/<url_hash>', methods=['POST'])
def submit(url_hash):
    if request.method == 'POST':
        print "Get data", request.form
        form = dumps(request.form)
        form_data = request.form.to_dict()
        form_data['submit_version'] = "UnderDevelopment"
        form_data['submit_user'] = current_user.username
        form_data['submit_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        mongo.db.demo.insert_one(form_data)
        flash(u'数据已经提交')
        if current_user.username == 'AnonymousUser':
            return redirect(url_for('survey.survey_publish', url_hash=url_hash))
        else:
            return redirect(url_for('survey.survey_user', url_hash = url_hash))
            