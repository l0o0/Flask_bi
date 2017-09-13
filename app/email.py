import requests
import os
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                    sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def sendcloud(to, subject, template, **kwargs):
    url = "http://api.sendcloud.net/apiv2/mail/send"
    html = render_template(template + '.html', **kwargs)
    txt = render_template(template + '.txt', **kwargs)
    # apikey = app.config['FLASK_SENDCLOUD_KEY']
    params = {"apiUser": os.getenv('apiUser'),
            "apiKey": os.getenv('apiKey'),
            "from":"1gb@1gene.com.cn",
            "to": to,
            "fromName": "1GB Admin",
            "subject": subject,
            "html": html,
            "plain": txt
            }

    def send(url, params):
        r = requests.post(url, data=params)
        return r

    thr = Thread(target=send, args=(url, params))
    thr.start()
    return thr
