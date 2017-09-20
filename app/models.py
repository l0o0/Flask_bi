from flask import current_app
from flask_login import current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from . import mongo
    


# User model for mongodb, for login_manager, validation and authorization.
class User(object):

    def __init__(self, user):
        for k,v in user.items():
            # mongo objectid can not convert to json.
            if k == '_id':
                continue
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

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.username})

    def token_confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.username:
            return False
        mongo.db.user.update_one({'username':self.username},{'$set':{'confirmed':True}})
        return True

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

    def generate_reset_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.username})

    def reset_password(self, token, password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.username:
            return False
        mongo.db.user.update_one({'username':self.username}, {'$set':{'password':password}})

        return True


class Permission(object):
    CREATE_FORM = 0x01
    MODIFY_FORM = 0x02
    VIEW_DATA = 0x04
    MODIFY_DATA = 0x08
    ADMINISTER = 0X80
        

class Role(object):
    def __init__(self, name):
        self.role = name
        roles = {
            'User':Permission.CREATE_FORM|Permission.MODIFY_FORM|Permission.VIEW_DATA,
            'Moderator':Permission.CREATE_FORM|Permission.MODIFY_FORM|Permission.VIEW_DATA|MODIFY_DATA,
            'Administer':0xff
        }
        self.permissions = roles[name]
        
    def can(self, permissions):
        return self.role is not None and (self.permissions & permissions) == permissions