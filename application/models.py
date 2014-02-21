"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class MerchantModel(ndb.Model):
    """Merchant Model"""
    merchant_name = ndb.StringProperty(required=True)
    merchant_cost = ndb.IntegerProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class ResultDataModel(ndb.Model):
    """Scraped data"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    merchants = ndb.TextProperty(required=True)