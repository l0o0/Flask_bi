from flask import render_template
from  . import main


@main.route('/')
def index():
    return '''<p>This is index.</p><p>
            <a href="/formbuilder" target="_blank">FormBuilder</a>
            <p><a href="/charts">Visit the charts blueprint.</a></p>'''
