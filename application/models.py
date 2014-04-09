"""
models.py

App Engine datastore models

"""


from google.appengine.ext import ndb


#-------------------------------------
# The data models
#-------------------------------------
class MerchantModel(ndb.Model):
    """Merchant Model"""
    merchant_name = ndb.StringProperty(required=True, default='')
    merchant_cost = ndb.StringProperty(required=True, default='')
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class ResultModel(ndb.Model):
    """Scraped data"""
    site_name = ndb.StringProperty(required=True, default='')
    merchants = ndb.TextProperty(required=True)
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


class SitesModel(ndb.Model):
    """Scraped sites with results id"""
    site_name = ndb.StringProperty(required=True, default='')
    results = ndb.TextProperty(required=True)


class BestbuyComModel(ndb.Model):
    """Bestbuy.Com Model
    Data format:
    """
    data = ndb.StringProperty(required=True, default='')
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


#-------------------------------------
# User model
#-------------------------------------
class User(ndb.Model):
    """Bestbuy.Com Model
    Data format:
    """
    name = ndb.StringProperty()
    email = ndb.StringProperty()

    openid = ndb.StringProperty()

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.name

