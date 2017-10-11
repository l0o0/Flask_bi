# -*- coding: utf-8 -*-

from flask import (render_template, request, url_for,
        abort)
from flask_login import (login_user, login_required, current_user)
from flask_pymongo import pymongo
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
    query = db.find({}).sort('_id', pymongo.ASCENDING)

    total = query.count()

    if offset > total:
        abort(404)

    start_id = query[offset]['_id']
    print offset, page, total, start_id
    items = db.find(
                    {'_id':{'$gte':start_id},}
                    ).sort('_id', pymongo.ASCENDING).limit(per_page)
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


# 接收dblist中返回的修改信息，保存至数据库
@database.route('/dbupdate', methods=['POST'])
@login_required
def dbupdate():
    if request.method == 'POST':
        formData = request.form.to_dict()
        return 'OK'
