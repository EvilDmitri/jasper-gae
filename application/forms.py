"""
forms.py

Web forms based on Flask-WTForms

See: http://flask.pocoo.org/docs/patterns/wtforms/
     http://wtforms.simplecodes.com/

"""

from flaskext import wtf
from flaskext.wtf import validators
from wtforms.ext.appengine.ndb import model_form

from .models import MerchantModel, ResultDataModel


class ClassicMerchantForm(wtf.Form):
    merchant_name = wtf.TextField('Name', validators=[validators.Required()])
    merchant_cost = wtf.TextAreaField('Pts/$', validators=[validators.Required()])


# App Engine ndb model form example
MerchantForm = model_form(MerchantModel, wtf.Form, field_args={
    'merchant_name': dict(validators=[validators.Required()]),
    'merchant_cost': dict(validators=[validators.Required()]),
})

# App Engine ndb model form example
ResultForm = model_form(ResultDataModel, wtf.Form, field_args={
    'merchants': dict(),
})