from flask import Blueprint 

# create formbuilder blueprint
survey = Blueprint('survey', __name__)
from . import views