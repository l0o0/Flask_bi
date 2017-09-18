# -*- coding:utf-8 -*-

from flask import render_template, url_for,abort, request
from flask_login import login_required, current_user
from bson.json_util import dumps
from  . import main
from .. import mongo
from main_city import main_city_ll

import random
from pyecharts import Scatter3D, Bar, Geo, Pie
from pyecharts.constants import DEFAULT_HOST
from flask import Flask, render_template

@main.route('/')
@login_required
def index():
    print 'index', current_user
    return render_template('index.html', menu="dashboard")

@main.route('/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = mongo.db.user.find_one({'username':username})
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/formtable', methods=['GET', 'POST'])
@login_required
def user_formtable():
    query = mongo.db.formtable.find({'username':current_user.username})
    return render_template('editable_table.html', query=query, menu='formtable')

@main.route('/post', methods=['POST'])
def post():
    print request.method
    print request.form
    return 'OK'
    
@main.route('/post/map', methods=['POST','GET'])
def map_post():
    query = mongo.db.demo.find({u'常住地：市':{'$ne':u'(空)'}},{'_id':0,u'常住地：市':1})
    cities = [x[u'常住地：市'] for x in query]
    data = [{'name':city, 'value':cities.count(city)} for city in set(cities)]
    geoCoordMap = {city:main_city_ll.get(city)  for city in set(cities)}
    print len(data)
    return 'ok'
    
    
@main.route("/test_chart")
def test_chart():
    plot = bar_plot()
    #query = mongo.db.demo.find({u'常住地：市':{'$ne':u'(空)'}},{'_id':0,u'常住地：市':1})
    #cities = [x[u'常住地：市'] for x in query]
    #data = [(city, cities.count(city)) for city in set(cities)]
    pie = pie_plot()
    scripts = set(plot.get_js_dependencies() + pie.get_js_dependencies())
    return render_template('charts/test2.html',
                           menu = 'charts', pie = pie.render_embed(),
                           myechart=plot.render_embed(),
                           host=DEFAULT_HOST,
                           script_list=scripts)

def pie_plot():
    query = mongo.db.demo.find({u'性别':{'$ne':u'(空)'}},{'_id':0,u'性别':1})
    data = [x[u'性别'] for x in query]
    attr = list(set(data))
    v1 = [data.count(x) for x in attr]
    print attr, v1
    pie = Pie(u'饼图', width=750)
    pie.add('', attr, v1, is_label_show=True)
    return pie
                           
                           
def scatter3d():
    data = [generate_3d_random_point() for _ in range(80)]
    range_color = [
        '#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf',
        '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
    scatter3D = Scatter3D("3D scattering plot demo", width=1200, height=600)
    scatter3D.add("", data, type='effectScatter', is_visualmap=True, visual_range_color=range_color)
    return scatter3D

def bar_plot():    
    attr = [u"衬衫", u"羊毛衫", u"雪纺衫", u"裤子", u"高跟鞋", u"袜子"]
    v1 = [5, 20, 36, 10, 75, 90]
    v2 = [10, 25, 8, 60, 20, 80]
    bar = Bar(u"柱状图数据堆叠示例", width=750)
    bar.add(u"商家A", attr, v1, is_stack=True)
    bar.add(u"商家B", attr, v2, is_stack=True)
    return bar
    
def generate_3d_random_point():
    return [random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)]