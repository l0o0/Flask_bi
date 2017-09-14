# -*- coding:utf-8 -*-

import json
import time
from base64 import urlsafe_b64encode as url_encode
from flask import (request, Response, render_template,
        redirect, url_for, flash)
from flask_login import current_user, login_required
from . import builder
from .. import mongo
from formbuilder import formLoader



mysession = {}
@builder.route('/')
@login_required
def formbuilder():
    return render_template('formbuilder/formbuilder.html')

@builder.route('/save', methods=['POST','GET'])
@login_required
def save():
    if request.method == 'POST':
        formData = request.form.get('formData')
        formDict = json.loads(formData)
        #print formDict
        if not formDict['fields']:
            flash(u'不能提交，保存空表格')
            return 'Empty form.'
        
        mysession['form_data'] = formData
        formDict['username']=current_user.username
        if not mongo.db.formtable.find_one({
                'username':current_user.username,
                'title':formDict['title']
                }):
            print 'create'
            formDict['createTime']= time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime()
                    )
            formDict['modifyTime']= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
            formDict['url_hash'] = url_encode(formDict['title'])
            mongo.db.formtable.insert_one(formDict)
            flash(u'表格信息已经保存')
        else:
            print 'update'
            mongo.db.formtable.update_one({
                    'username':current_user.username,
                    'title':formDict['title']
                    }, 
                    {'$set': {
                            'fields': formDict['fields'],
                            'modifyTime':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            }
                    }
            )                
            flash(u'表格信息已经更新')        
                            
        return 'OK'


# this url should be checked if have more user.
@builder.route('/render')
def render():
    if not mysession.get('form_data'):
        return redirect(url_for('builder.formbuilder'))

    form_data = mysession.get('form_data')
    mysession['form_data'] = None

    form_loader = formLoader(form_data, url_for('builder.submit_test'))
    render_form = form_loader.render_form()

    return render_template('formbuilder/render.html', render_form=render_form)

@builder.route('/submit_test', methods=['POST'])
def submit_test():
    if request.method == 'POST':
        print request.form
        form = json.dumps(request.form)
        return form
        

@builder.route('/submit_test', methods=['POST'])