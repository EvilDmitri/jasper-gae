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
from models import MerchantModel, ResultDataModel


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


def home():
    return redirect(url_for('list_results'))


@login_required
def list_results():
    """List all scraped data"""
    results = ResultDataModel.query()

    return render_template('list_data.html', results=results)


def grab():
    # Grab data
    print 'yo'
    grabber = UltimateRewardsGrabber()
    grabber.grab()
    flash(u'Successfully grabbed')
    return 'OK'


@login_required
def delete_merchant(result_id):
    """Delete an results object"""
    merchant = ResultDataModel.get_by_id(result_id)
    try:
        merchant.key.delete()
        flash(u'result %s successfully deleted.' % result_id, 'success')
        return redirect(url_for('list_results'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_results'))


@login_required
def list_merchants():
    """List all merchants"""
    merchants = MerchantModel.query()
    form = MerchantForm()
    if form.validate_on_submit():
        merchant = MerchantModel(
            merchant_name=form.merchant_name.data,
            merchant_cost=form.merchant_cost.data,
            # added_by=users.get_current_user()
        )
        try:
            merchant.put()
            merchant_id = merchant.key.id()
            flash(u'merchant %s successfully saved.' % merchant_id, 'success')
            return redirect(url_for('list_merchants'))
        except CapabilityDisabledError:
            flash(u'App Engine Datastore is currently in read-only mode.', 'info')
            return redirect(url_for('list_merchants'))

    return render_template('list_merchants.html', merchants=merchants, form=form)


@login_required
def edit_merchant(merchant_id):
    merchant = MerchantModel.get_by_id(merchant_id)
    form = MerchantForm(obj=merchant)
    if request.method == "POST":
        if form.validate_on_submit():
            merchant.merchant_name = form.data.get('merchant_name')
            merchant.merchant_cost = form.data.get('merchant_cost')
            merchant.put()
            flash(u'merchant %s successfully saved.' % merchant_id, 'success')
            return redirect(url_for('list_merchants'))
    return render_template('edit_merchant.html', merchant=merchant, form=form)


@login_required
def delete_merchant(merchant_id):
    """Delete an merchant object"""
    merchant = MerchantModel.get_by_id(merchant_id)
    try:
        merchant.key.delete()
        flash(u'merchant %s successfully deleted.' % merchant_id, 'success')
        return redirect(url_for('list_merchants'))
    except CapabilityDisabledError:
        flash(u'App Engine Datastore is currently in read-only mode.', 'info')
        return redirect(url_for('list_merchants'))


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

