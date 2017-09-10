from flask import render_template
from  . import main


@main.route('/')
def index():
    return 'This is index.<a href="/formbuilder" target="_blank">FormBuilder</a>'
