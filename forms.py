from google.appengine.ext import ndb
from wtforms import form, fields, validators
from application.models import User


class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        q = "SELECT * FROM ResultModel  WHERE login = '%s'" % self.login.data
        user = ndb.gql(q).fetch()
        return user


class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        pass
        # if db.session.query(User).filter_by(login=self.login.data).count() > 0:
        #     raise validators.ValidationError('Duplicate username')
