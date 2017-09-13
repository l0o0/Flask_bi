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
from ..email import sendcloud


class User():

    def __init__(self, user):
        for k,v in user.items():
            setattr(self, k, v)
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_confirmed(self):
        return self.confirmed
        
    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
    
    def get_id(self):
        return self.username    
    
    def verify_password(self, input):
        print self.password_hash, input
        print check_password_hash(self.password_hash, input)
        return check_password_hash(self.password_hash, input)
    
    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.username:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        elif mongo.db.user.find_one({'email':new_email}) is not None:
            return False
        #self.avatar_hash = hashlib.md5(self.email.encoding('utf-8')).hexdigest()
        mongo.db.user.update_one({'username':self.username},{'$set':{'email':new_email}})
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.username, 'new_email': new_email})
        
    
@login_manager.user_loader
def load_user(username):
    user = mongo.db.user.find_one({"username": username})
    if not user:
        return None
    user.pop('_id')
    print '1 user loader_user',user
    return User(user)

# auth verify and email confirm
def generate_confirmation_token(username, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'confirm':username})

def token_confirm(username, token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False
    if data.get('confirm') != username:
        return False
    mongo.db.user.update_one({'username':username},{'$set':{'confirmed':True}})
    return True

def generate_reset_token(username,expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'reset': username})
    
def reset_password(username, token, password):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False
    if data.get('reset') != username:
        return False
    mongo.db.user.update_one({'username':username}, {'$set':{'password':password}})
    
    return True


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
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.user.find_one({'email':form.email.data})      
        # _id is can not convert to json
        user.pop('_id')
        if user is not None and check_password_hash(user['password_hash'],form.password.data):
            login_user(User(user), form.remember_me.data)
            print current_user.is_authenticated
            print 'request', request.args.get('next')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = dict(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    password_hash = generate_password_hash(form.password.data),
                    confirmed=False)
        mongo.db.user.insert_one(user)
        token = generate_confirmation_token(user['username'])
        sendcloud(user['email'], u'账户管理信息',
                    'auth/email/confirm', user=user, token=token)
        flash(u"一封确认邮件已经飞向邮箱")
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
#@login_required
def confirm(token):
    s= Serializer(current_app.config['SECRET_KEY'])
    try:
        user = s.loads(token)['confirm']
    except:
        abort(404)
    user = mongo.db.user.find_one_or_404({"username":user})
    if user['confirmed']:
        return redirect(url_for('main.index'))
    print 'token confirm', token_confirm(user['username'], token)
    if token_confirm(user['username'], token):
        flash('You have confirmed your account, Thanks!')
        return redirect(url_for('auth.login'))
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.username)
    sendcloud(current_user.email, 'Confirm Your Account',
                'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


# for password change
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
            flash('Your password have been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change_password.html', form=form)


# Reset password by email.
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:   # vist as anonymous user
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = mongo.db.user.find_one({'email':form.email.data})
        if user:
            token = generate_reset_token(user['username'])
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
        if reset_password(user['username'], token, form.password.data):
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
        print form.password.data
        print current_user.password
        print current_user.verify_password(form.password.data)
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            sendcloud(new_email, 'Confirm your email address',
                'auth/email/change_email', user=current_user, token=token)
            flash(u"An email with instructions to confirm your new email "
                "address has been sent to you.")
            return redirect(url_for('main.index'))
        else:
            flash(u'密码错误')
    return render_template('auth/change_email.html', form=form)



@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):       
        flash('邮箱已经更新')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
