"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class MerchantModel(ndb.Model):
    """Merchant Model"""
    merchant_name = ndb.StringProperty(required=True)
    merchant_cost = ndb.TextProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
