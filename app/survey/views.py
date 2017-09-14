from base64 import urlsafe_b64decode as url_decode
from bson.json_util import loads, dumps
from flask import request, url_for, render_template
from . import survey
from .. import mongo
from ..formbuilder.formbuilder import formLoader


@survey.route('/<user>/<hash>', methods=['POST','GET'])
def publish(user, hash):
    print type(hash)
    title = url_decode(hash.encode('utf-8'))
    formData = mongo.db.formtable.find_one({'username':user,'title':title})
    formData = dumps(formData)
    form_loader = formLoader(formData, url_for('survey.submit'))
    render_form = form_loader.render_form()
    return render_template('formbuilder/render.html', render_form=render_form)

@survey.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        form = dumps(request.form)
        #mongo.db.survey.insert_one(request.form)
        return form