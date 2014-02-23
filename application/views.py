"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For merchant the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from application.grabber.scrape import UltimateRewardsGrabber
from decorators import login_required, admin_required
from models import MerchantModel, ResultModel, SitesModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)

URLS_SHOPPING = {
        'ultimaterewardsearn.chase.com': 'http://ultimaterewardsearn.chase.com/shopping',
        'aadvantageeshopping.com': 'https://www.aadvantageeshopping.com/shopping/b____alpha.htm',
        # 'dividendmilesstorefront.com': 'https://www.dividendmilesstorefront.com/shopping/b____alpha.htm',
        'onlinemall.my.bestbuy.com': 'https://onlinemall.my.bestbuy.com/shopping/b____alpha.htm',
        'mileageplusshopping.com': 'https://www.mileageplusshopping.com/shopping/b____alpha.htm',
        'mileageplanshopping.com': 'https://www.mileageplanshopping.com/shopping/b____alpha.htm',
        'rapidrewardsshopping.southwest.com': 'https://rapidrewardsshopping.southwest.com/shopping/b____alpha.htm',
    }


def home():
    return redirect(url_for('sites'))


def sites():
    """List of sites to show"""
    sites_list = SitesModel.query()
    site_names = URLS_SHOPPING.keys()
    return render_template('sites.html', site_names=site_names, sites=sites_list)


def list_results():
    """List all scraped data"""
    results = ResultModel.query()
    return render_template('list_data.html', results=results)


def show_result(result_id):
    """List all scraped data"""
    result = ResultModel.get_by_id(result_id)
    result = result.merchants
    data = result.split(r'\n')
    merchants = dict()

    for string in data:
        data = string.split(r'\t')
        merchants[data[0]] = data[1]
    print merchants
    return render_template('list_merchants.html', merchants=merchants)


def delete_result(result_id):
    """Delete an results object"""
    result = ResultModel.get_by_id(result_id)
    try:
        result.key.delete()
        flash(u'result %s successfully deleted.' % result_id, 'success')
        return redirect(url_for('list_results'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_results'))


def list_merchants():
    """List all merchants"""
    merchants = MerchantModel.query()
    return render_template('list_merchants.html', merchants=merchants)


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


@cache.cached(timeout=60)
def cached_merchants():
    """This view should be cached for 60 sec"""
    merchants = MerchantModel.query()
    return render_template('list_merchants_cached.html', merchants=merchants)


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''


def grab():
    # Grab data
    if request.method == 'POST':
        site_name = request.form['site_name']
        print site_name
        print '----------------'
        grabber = UltimateRewardsGrabber(site_name)
        result_id = grabber.grab()
        flash(u'Successfully grabbed')
        return result_id