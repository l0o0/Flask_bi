from flask import Blueprint

database = Blueprint('database', __name__)
from . import views
