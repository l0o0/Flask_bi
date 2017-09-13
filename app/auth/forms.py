# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from .. import mongo


class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64, Email())])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64),
                        Email()])
    username = StringField('Username', validators=[Required(), Length(1,64),
                        ])
    password = PasswordField('Password', validators=[Required(),
                            EqualTo('password2', message='Password must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        if mongo.db.user.find_one({'email': field.data}):
            raise ValidationError('Email already registered.')

    def validat_username(self, field):
        if mongo.db.user.find_one({'username':field.data}).first():
            raise ValidationError('Username already registered.')


class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[Required(),
        EqualTo('password2', message="Passwords must math")])
    password2 = PasswordField('Confirm your password', validators=[Required()])
    submit = SubmitField('Update password')


class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    submit = SubmitField('Reset Passowrd')


class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('New Password', validators=[Required(),
        EqualTo('passowrd2', message='Passwords must match')])
    passowrd2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if mongo.db.user.find_one({'email': field.data}) is None:
            raise ValidationError('Unknown email address.')


class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if mongo.db.user.find_one({'email': field.data}):
            raise ValidationError(u'邮箱已经被注册')
