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
from forms import MerchantForm
from models import MerchantModel, ResultDataModel, ResultModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
    return redirect(url_for('list_results'))


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
    grabber = UltimateRewardsGrabber()
    result_id = grabber.grab()
    flash(u'Successfully grabbed')
    return result_id