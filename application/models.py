"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


class MerchantModel(ndb.Model):
    """Merchant Model"""
    merchant_name = ndb.StringProperty(required=True, default='')
    merchant_cost = ndb.IntegerProperty(required=True, default='')
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class ResultDataModel(ndb.Model):
    """Scraped data"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    site_name = ndb.StringProperty(required=True, default='')
    merchants = ndb.TextProperty(required=True)


class ResultModel(ndb.Model):
    """Scraped data"""
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    site_name = ndb.StringProperty(required=True, default='')
    merchants = ndb.TextProperty(required=True)