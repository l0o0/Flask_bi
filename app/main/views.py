from flask import render_template
from flask_login import login_required, current_user
from  . import main


@main.route('/')
def index():
    print 'index', current_user
    return render_template('index.html')
