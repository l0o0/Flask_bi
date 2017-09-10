from flask import Blueprint 

# create formbuilder blueprint
builder = Blueprint('builder', __name__)
from . import views
