# -*- coding:utf-8 -*-

import json
import time
from base64 import urlsafe_b64encode as url_encode
from flask_pymongo import pymongo
from flask import (request, Response, render_template,
        redirect, url_for, flash, session, abort)
from flask_login import current_user, login_required
from flask_paginate import Pagination
from . import builder
from .. import mongo
from ..utils import paginate
from formbuilder import formLoader


# 对提高的调查问卷数据进行格式化，把一些多项选择的结果放到一个Python list中
def reformat(form):
    newForm = {}
    for k, v in form.items():
        newKey = k.split('_')[0]
        if newKey in newForm:
            tmpValue = newForm[newKey]
            if not isinstance(tmpValue, list):
                tmpValue = [tmpValue]
            tmpValue.append(v)
            newForm[newKey] = tmpValue
        else:
            newForm[newKey] = v
    return newForm



@builder.route('/')
@login_required
def formbuilder(data=None):
    if not data:
        data = u'{"fields": [], "description": "这里可以填写表格的相关说明，在数据库查询中是根据表格名称进行查询，请不要使用相同的表格名称，以免出现数据被覆盖。不用使用英文的单双引号，会导致数据传递错误", "title": "表格名称。"}'
    return render_template('formbuilder/formbuilder.html', init_form=data)

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

        session['form_data'] = formData
        formDict['username']=current_user.username
        # 根据用户名和表格的title来查询数据库
        # 如果调查表已经存在就更新，如果不存在就创建
        if not mongo.db.formtable.find_one({
                'username':current_user.username,
                'title':formDict['title']
                }):
            print 'survery form create'
            formDict['createTime']= time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime()
                    )
            formDict['modifyTime']= time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            formDict['public'] = False  # 调查问卷默认是不允许被外部非注册人员访问的
            mongo.db.formtable.insert_one(formDict)
            flash(u'表格信息已经保存')
        else:
            print 'survey form update'
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
        init_form = json.JSONEncoder().encode(session['form_data'])
        return render_template('formbuilder/formbuilder.html', init_form=init_form)


# this url should be checked if have more user.
@builder.route('/render')
def render():
    if not session.get('form_data'):
        return redirect(url_for('builder.formbuilder'))

    form_data = session.get('form_data')
    session['form_data'] = None

    form_loader = formLoader(form_data, url_for('builder.submit_test'))
    render_form = form_loader.render_form()

    return render_template('formbuilder/render.html', render_form=render_form)


# Display form table list. 处理分布的展示效果
@builder.route('/formlist/<int:page>', methods=['GET', 'POST'])
@login_required
def formlist(page=1):
    session['page'] = page
    per_page = current_user.pagesize
    #per_page = 1
    offset = per_page * (page-1)

    query = mongo.db.formtable.find(
                                    {'username':current_user.username}
                                   ).sort('_id', pymongo.ASCENDING)

    total = query.count()
    if total == 0:
        return u'空空如也'
    if offset > total:
        abort(404)

    start_id = query[offset]['_id']
    items = mongo.db.formtable.find(
                                    {'username':current_user.username,
                                     '_id':{'$gte':start_id}}
                                   ).sort('_id', pymongo.ASCENDING).limit(per_page)


    pagination = paginate(page, per_page, total)
    #print start_id, offset, page, total,
    return render_template(
                            'formbuilder/formlist.html',
                            page=page,
                            per_page=per_page,
                            total=total,
                            items = items,
                            pagination = pagination
                          )


# 对接builder.formlist Edit中的保存按钮
# Update the form table in the formlist view.
@builder.route('/formlist_update', methods=['POST'])
@login_required
def formlist_update():
    if request.method == 'POST':
        formData = request.form.to_dict()
        #print formData
        formData['createTime']= time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime()
                    )
        mongo.db.formtable.update_one({'username' : current_user.username,
                                'title' : formData['title']},
                                {'$set' : formData }
                                )
        flash(u'调查问卷已更新')
        return redirect(url_for('builder.formlist', page=session['page']))


# builder.formlist 中表格的edit按钮的功能
@builder.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    # print request.method
    if request.method == 'POST':        # 删除选项
        postData = request.form.to_dict()
        # print args
        #mongo.db.formtable.delete_one(postData)
        flash(u'调查问卷已经删除')
        return 'deletion done', 200

    else:       # 重新设计选项
        args = request.args.to_dict()
        formData = mongo.db.formtable.find_one(args)
        formData.pop('_id')
        init_form = json.dumps(formData)
        return render_template('formbuilder/formbuilder.html', init_form=init_form)


@builder.route('/submit_test', methods=['POST'])
def submit_test():
    if request.method == 'POST':
        #print request.form
        #print reformat(request.form)
        form = json.dumps(request.form)
        formFormated = json.dumps(reformat(request.form))
        return "<p>Origin: %s</p><p>Reformat: %s</p>" % (form, formFormated)
