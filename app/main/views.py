# -*- coding:utf-8 -*-

import time
from flask import (render_template, url_for,abort, 
                request, redirect)
from flask_login import login_required, current_user
from bson.json_util import dumps
from  . import main
from .. import mongo
from ..models import permission_required, admin_required
from main_city import main_city_ll

import random
from pyecharts import Scatter3D, Bar, Geo, Pie
from pyecharts.constants import DEFAULT_HOST
from flask import Flask, render_template


@main.route('/')
@login_required
def index():
    #print 'index', current_user.username
    return render_template('index.html')

    
@main.route('/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = mongo.db.user.find_one({'username':username})
    if user is None:
        abort(404)
    return render_template('user.html', user=user)
    
    
@main.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin():
    return 'OK'

    

    
    