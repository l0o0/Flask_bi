# -*- coding: utf-8 -*-
import json
from bson import ObjectId
from flask import (render_template, request, url_for,
        abort, flash, jsonify)
from flask_login import (login_user, login_required, current_user)
from . import database
from .. import mongo
from ..utils import paginate


# 列出数据库中的数据，并可以对数据进行修改
@database.route('/dblist/<int:page>', methods=['GET', 'POST'])
@login_required
def dblist(page=1):
    per_page = current_user.pagesize
    offset = per_page * (page-1)

    db = mongo.db.worldbank
    query = db.find({}).sort('_id', 1)

    total = query.count()

    if offset > total:
        abort(404)

    start_id = query[offset]['_id']
    print offset, page, total, start_id
    items = db.find(
                    {'_id':{'$gte':start_id},}
                    ).sort('_id', 1).limit(per_page)
    print items.count()
    pagination = paginate(page, per_page, total)
    return render_template(
            'database/dblist.html',
            page=page,
            per_page=per_page,
            total=total,
            items=items,
            pagination=pagination
    )


# 接收过滤的条件，对条件进行处理，并返回对应的结果
@database.route('/query', methods=['POST', 'GET'])
@database.route('/query/<int:page>', methods=['POST', 'GET'])
@login_required
def query(page=1):
    per_page = current_user.pagesize
    offset = per_page * (page-1)

    db = mongo.db.worldbank

    # filterSQL = {'action': u'query-test', 'sql': u"{'sort':{'borrower':1}}"}
    filterSQL = request.form.to_dict()
    print filterSQL
    # 将单引号替换为双引号进行json转换
    sql = filterSQL['sql'].replace("'", '"')
    sql = json.loads(sql)
    sql_sort = sql.get('sort',{'_id':1})    # 默认按照_id进行升序
    
    if 'sort' in sql:
        del sql['sort']
        
    # 返回测试结果
    if filterSQL.get('action') == 'query-test':
        query = db.find(sql).sort(sql_sort.items())
        return 'ok, query number is %s' % query.count()
    # 返回查询结果
    if filterSQL.get('action') == 'query-submit':
        query = db.find(sql).sort('_id', 1)
        total = query.count()
        if offset > total:
            abort(404)
        start_id = query[offset]['_id']
        sql['_id'] = {'$gte':start_id}
        items = db.find(sql).sort(sql_sort.items()).limit(per_page)
        pagination = paginate(page, per_page, total)
        return render_template(
                'database/dblist.html',
                page=page,
                per_page=per_page,
                total=total,
                items=items,
                pagination=pagination,
                sql=filterSQL['sql']
        )


# 接收dblist中返回的修改信息，保存至数据库
@database.route('/dbupdate', methods=['POST'])
@login_required
def dbupdate():
    if request.method == 'POST':
        formData = request.form.to_dict()
        print formData
        db = mongo.db.worldbank
        # 如果formData中只有一个id的key，说进行删掉操作，从数据库中进行删除
        # 如果是其他情况，就对数据库的信息进行更新
        if len(formData) == 1 and 'id' in formData:
            item_id = ObjectId(formData['id'].strip())
            db.delete_one({'_id':item_id})
            flash(u'删除成功')
            return 'deletion done', 200
        else:
            return 'update done', 200

# 用于查询数据
@database.route('/api', methods=['POST'])
@login_required
def api():
    if request.method == 'POST':
        postData = request.form.to_dict()
        print postData
        _id = ObjectId(postData['id'].strip())
        db = mongo.db.worldbank
        query = db.find_one({'_id':_id})
        query['id'] = str(query['_id'])
        del query['_id']
        return jsonify(query),200
