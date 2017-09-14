from flask import render_template, url_for,abort
from flask_login import login_required, current_user
from bson.json_util import dumps
from  . import main
from .. import mongo


@main.route('/')
@login_required
def index():
    print 'index', current_user
    return render_template('index.html')

@main.route('/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = mongo.db.user.find_one({'username':username})
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/<username>/formtable', methods=['GET', 'POST'])
@login_required
def user_formtable(username):
    user = mongo.db.user.find_one({'username':username})
    if user is None:
        abort(404)
    metadata = [
        {"name":"username","label":"NAME","datatype":"string","editable":'true'},
        {"name":"title","label":"TITLE","datatype":"string","editable":'true'},
        {"name":"description","label":"DESC","datatype":"string","editable":'true'},
        {"name":"create","label":"CREATE","datatype":"string","editable":'true'},
        {"name":"modify","label":"MODIFY","datatype":"string","editable":'true'}
        ]
    formtable = mongo.db.formtable.find({'username':username},
                                        {'username':1,
                                        'title':1,
                                        'description':1,
                                        'createTime':1,
                                        'modifyTime':1,'_id':0})
    data = []
    for i,row in enumerate(formtable):
        row['id']=i+1
        data.append(row)
        print row['title']
    print data
    jsondata = {'metadata':metadata, 'data':data}
    print jsondata
    string = dumps(jsondata)
    print string
    return render_template('formtable.html', formtable=string)
