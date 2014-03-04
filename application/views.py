"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For merchant the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""
import datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import request, render_template, flash, url_for, redirect

from flask_cache import Cache

from application import app
from application.grabber.scrape import UltimateRewardsGrabber, XmlGrabber, ShopGrabber, BestbuyGrabber
from decorators import login_required, admin_required
from models import MerchantModel, ResultModel, SitesModel

from collections import OrderedDict

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)


URLS = [
    'ultimaterewardsearn.chase.com',
    'aadvantageeshopping.com',
    'dividendmilesstorefront.com',
    'onlinemall.my.bestbuy.com',
    'mileageplusshopping.com',
    'mileageplanshopping.com',
    'rapidrewardsshopping.southwest.com',
    'barclaycardrewardsboost.com',
    'skymilesshopping.com',

    'shop.upromise.com',

    'discover.com',

    # 'www.bestbuy.com'
]

#
# def home():
#     return redirect(url_for('test'))


def sites():
    """List of sites to show"""
    sites_list = SitesModel.query()
    return render_template('sites.html', site_names=URLS, sites=sites_list)


def list_results():
    """List all scraped data"""
    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    return render_template('list_data.html', site_names=URLS, results=results)


def show_result(result_id):
    """List all scraped data"""
    result = ResultModel.get_by_id(result_id)
    print result
    result = result.merchants
    data = result.split(r'\n')
    merchants = dict()

    for string in data:
        data = string.split(r'\t')
        merchants[data[0]] = data[1]
    return render_template('list_merchants.html', site_names=URLS, merchants=merchants)


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


def test():
    """Test the new look"""
    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    return render_template('test.html', site_names=URLS, results=results)


#------------------------------------------
# Main page
#------------------------------------------
def test_result(result_id):
    """Main page"""
    result = ResultModel.get_by_id(int(result_id))

    date = result.timestamp

    data = []
    site = ''
    result = result.merchants
    lines = result.split(r'\n')
    for line in lines:
        items = line.split(r'\t')
        if len(items) == 6:
            site = 'apple'      # This is needed for 'www.bestbuy.com'
        data.append(items)

    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    return render_template('test.html', site_names=URLS, results=results, merchants=data, date=date, site=site)


def by_time():
    """Response up to 5 last 5 results"""
    site = ''
    if request.method == 'POST':
        start_time = request.form['start_time']  # {0}
        # start_time = datetime.datetime(start_time).strptime()
    else:
        start_time = datetime.datetime.now()
    # end_time = start_time - datetime.timedelta(days=5)  # {1}
    # q = "SELECT * FROM ResultModel WHERE timestamp < DATETIME({0}) AND  timestamp > DATE({1})".format(
    # start_time, end_time)

    date = start_time.strftime('%Y-%m-%d %H:%M:%S')
    # q = "SELECT * FROM ResultModel  WHERE timestamp <= DATETIME('%s')" % date
    # data_entries = ndb.gql(q).fetch()
    # print(q)

    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    return render_template('test.html', site_names=URLS, results=results,  site=site)


#------------------------------------------
# Method list all last results
#------------------------------------------
def all_malls():
    """Response all malls from last job"""
    start_time = datetime.datetime.now()
    sites_result = OrderedDict()
    for url in URLS:
        sites_result[url] = ''

    date = start_time.strftime('%Y-%m-%d %H:%M:%S')

    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    last_results = results[-10:]
    data_entries = last_results

    data = OrderedDict([[x, ''] for x in URLS])
    sources = []
    data = dict()
    for entry in data_entries:
        date_scraped = entry.timestamp
        scraped_from = entry.site_name
        sources.append('\n'.join([scraped_from, date_scraped.strftime('%Y-%m-%d %H:%M:%S')]))
        vendors = entry.merchants
        vendors = vendors.split(r'\n')

        for vendor in vendors:
            result = vendor.split(r'\t')

            name = result[0]
            try:
                rate = result[1]
            except ValueError:
                rate = 'NNNN'

            try:    # If this vendor is listed
                rates = data[name]
            except KeyError:
                rates = sites_result
            rates[scraped_from] = rate

            data[name] = rates

    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    return render_template('all_malls.html', site_names=URLS, results=results, date=date, dates=URLS, data=data, site='')

#------------------------------------------
# Method run grabber from web-page
#------------------------------------------
def grab():
    # Grab data
    if request.method == 'POST':
        site_name = request.form['site_name']

        if 'discover.com' in site_name:
            grabber = XmlGrabber(site_name)
        elif 'shop.upromise.com' in site_name:
            grabber = ShopGrabber(site_name)
        elif 'www.bestbuy.com' in site_name:
            grabber = BestbuyGrabber(site_name)
        else:
            grabber = UltimateRewardsGrabber(site_name)

        result_id = grabber.grab()
        flash(u'Successfully grabbed')
        return result_id


#------------------------------------------
# Method for Cron job to everyday scraping
#------------------------------------------
def grab_daily():
    success = 0
    for site_name in URLS:
        if 'discover.com' in site_name:
            grabber = XmlGrabber(site_name)
        elif 'shop.upromise.com' in site_name:
            grabber = ShopGrabber(site_name)
        # elif 'www.bestbuy.com' in site_name:
        #     grabber = BestbuyGrabber(site_name)
        else:
            grabber = UltimateRewardsGrabber(site_name)

        if grabber.grab():
            success += 1
    return 'OK'