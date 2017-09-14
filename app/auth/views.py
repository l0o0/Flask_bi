# -*- coding: utf-8 -*-

from flask import (render_template, redirect, request, url_for,
        flash, abort, current_app)
from flask_login import (login_user, login_required,
        logout_user, current_user)
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import auth
from .forms import (LoginForm, RegistrationForm, ChangePasswordForm,
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm)
from .. import mongo, login_manager
from ..models import User
from ..email import sendcloud


@login_manager.user_loader
def load_user(username):
    user = mongo.db.user.find_one({"username": username})
    if not user:
        return None
    user.pop('_id')
    return User(user)

# auth verify and email confirm
def generate_confirmation_token(username, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'confirm':username})


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.is_confirmed \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.is_confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    print request.form
    print request.method
    if request.method == "POST":
        form = request.form
        user = mongo.db.user.find_one({'email':form.get('email')})
        if user is not None and check_password_hash(user['password_hash'],form.get('password')):
            login_user(User(user), form.get('remember_me'))
            return redirect(url_for('main.index'))
        flash(u'邮箱或密码错误')
    return render_template('auth/login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'退出成功')
    return redirect(url_for('main.index'))


@auth.route('/registre', methods=['GET', 'POST'])
def registre():
    #form = RegistrationForm()
    if request.method == 'POST':
        form = request.form
        user = dict(email=form.get('email'),
                    username=form.get('username'),
                    password=form.get('password'),
                    password_hash = generate_password_hash(form.get('password')),
                    confirmed=False)
        mongo.db.user.insert_one(user)
        token = generate_confirmation_token(user['username'])
        sendcloud(user['email'], u'账户管理信息',
                    'auth/email/confirm', user=user, token=token)
        flash(u'一封确认邮件已经飞向邮箱')
        return redirect(url_for('main.index'))
    return render_template('auth/registre.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    s= Serializer(current_app.config['SECRET_KEY'])
    try:
        user = s.loads(token)['confirm']
    except:
        abort(404)
    user = mongo.db.user.find_one_or_404({"username":user})
    if user['confirmed']:
        return redirect(url_for('main.index'))
    if current_user.token_confirm(token):
        flash(u'账户已确认')
        return redirect(url_for('auth.login'))
    else:
        flash(u'链接失效')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    sendcloud(current_user.email, 'Confirm Your Account',
                'auth/email/confirm', user=current_user, token=token)
    flash(u'确认邮件已经发送，请按照邮件提示进行操作')
    return redirect(url_for('main.index'))


# for password change when you have login in.
@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            mongo.db.user.update_one(
                {'username':current_user.username},
                {'$set':{'password':form.password.data}}
                )
            mongo.db.user.update_one(
                {'username':current_user.username},
                {'$set':{'password_hash':generate_password_hash(form.password.data)}}
                )
            flash(u'密码已更新')
            return redirect(url_for('main.index'))
        else:
            flash(u'密码错误')
    return render_template('auth/change_password.html', form=form)


# Reset password by email when you forget password.
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:   # vist as anonymous user
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = mongo.db.user.find_one({'email':form.email.data})
        if user:
            token = current_user.generate_reset_token()
            sendcloud(user.email, 'Reset Your Passowrd',
                        'auth/email/reset_password', user=user, token=token,
                        next=request.args.get('next'))
            flash("An email with instructions to reset your passowrd has been"
                "sent to you.")
            return redirect(url_for('auth.login'))
        else:
            flash(u'该邮箱还未被注册！')
    return render_template('auth/reset_password.html', form=form)


# Handle the request in the password-reset email
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = mongo.db.user.find_one({'email':form.email.data})
        if user is None:
            return redirect(url_for('main.index'))
        if current_user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)



# Change email Address
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            sendcloud(new_email, 'Confirm your email address',
                'auth/email/change_email', user=current_user, token=token)
            flash(u"确认邮件已经发送，请按照提示进行操作确认")
            return redirect(url_for('main.index'))
        else:
            flash(u'密码错误')
    return render_template('auth/change_email.html', form=form)



@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(u'邮箱已更新')
    else:
        flash(u'请求失效')
    return redirect(url_for('main.index'))
