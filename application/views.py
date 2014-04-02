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
from application.grabber.scrape import UltimateRewardsGrabber, XmlGrabber, ShopGrabber, \
                                    BestbuyGrabber, RetailersGrabber, get_data_from_html
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

    'shop.amtrakguestrewards.com',
    'shop.lifemiles.com'
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

    # Should delete result from site model
    site = result.site_name
    q = "SELECT * FROM ResultModel  WHERE site_name = '%s'" % site
    data_entry = ndb.gql(q).fetch()
    results = data_entry.results.split('/')
    for result in results:
        if str(result_id) in result:
            results.remove(result)
    data_entry.results = '/'.join(results)
    data_entry.put()

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
    site = result.site_name
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

    date = start_time.strftime('%Y-%m-%d %H:%M:%S')

    results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    last_results = results[-10:]
    data_entries = last_results

    sites = OrderedDict([[x, ' '] for x in URLS])
    headers = OrderedDict([[x, ' '] for x in URLS])
    data = dict()
    for entry in data_entries:
        date_scraped = entry.timestamp
        scraped_from = entry.site_name
        # Table header
        headers[scraped_from] = ('\n'.join([scraped_from, date_scraped.strftime('%Y-%m-%d %H:%M:%S')]))

        vendors = entry.merchants
        vendors = vendors.split(r'\n')

        for vendor in vendors:
            result = vendor.split(r'\t')

            name = result[0]
            try:
                rate = result[1]
            except ValueError:
                rate = ' '

            try:    # If this vendor is listed
                rates = data[name]
            except KeyError:
                rates = sites
            rates[scraped_from] = rate

            data[name] = rates

    # for vendor in data:
    #     rates = data[vendor]
    #     res = []
    #     for rate in rates:
    #         rate = rates[rate]
    #         res.append(rate)
    #     print vendor, ' - ', res
    # print '----------'
    # results = ResultModel.query().order(-ResultModel.timestamp).fetch()
    return render_template('all_malls.html', site_names=URLS,
                           date=date,
                           headers=headers, data=data,
                           site='')

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
        elif site_name in ['shop.amtrakguestrewards.com', 'shop.lifemiles.com']:
            grabber = RetailersGrabber(site_name)
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

        elif site_name in ['shop.amtrakguestrewards.com', 'shop.lifemiles.com']:
            grabber = RetailersGrabber(site_name)
        # elif 'www.bestbuy.com' in site_name:
        #     grabber = BestbuyGrabber(site_name)
        else:
            grabber = UltimateRewardsGrabber(site_name)

        if grabber.grab():
            success += 1
    return 'OK'


#------------------------------------------
# Method for check last result with previous
#------------------------------------------
def check_modification():
    def get_data(result_id):
        """Get data from DB by id
        Return dictionary with 'name': 'rate'
        """
        result = ResultModel.get_by_id(int(result_id))
        try:
            result = result.merchants
        except AttributeError:
            return False

        data = result.split(r'\n')
        merchants = dict()
        for item in data:
            res = item.split(r'\t')
            name = res[0]
            rate = res[1].split(' ')[0]
            merchants[name] = rate
        return merchants

    def compare_data(last, prev):
        """Receive two dictionary with 'name': 'rate'
        If some of them is changed should alert?
        """
        list_of_changes = []
        for name in last:
            last_rate = last[name]
            try:
                prev_rate = prev[name]
                if last_rate != prev_rate:
                    changed = name + ' ' + prev_rate + '/' + last_rate
                    list_of_changes.append(changed)
            except KeyError:
                changed = name + ' ' + ' ' + '/' + last_rate
                list_of_changes.append(changed)

        return list_of_changes

    sites = SitesModel.query().order().fetch()
    changed_sites = OrderedDict([[x, ' '] for x in URLS])
    for site in sites:
        results = site.results
        lasts = results.split('/')
        if len(lasts) < 2:
            # Only one result
            continue

        last = lasts[-1].split('|')[0]  # [1] - timestamp
        last_result = get_data(last)

        i = -2
        while True:
            prev = lasts[i].split('|')[0]
            prev_result = get_data(prev)
            if prev_result:
                break
            i -= 1
        # Now we have IDs

        changes = compare_data(last_result, prev_result)
        if len(changes) > 0:
            changed_sites[site.site_name] = changes

    # Mail results
    from mailer.mail_send import SendStatistics
    stat = False
    for val in changed_sites.itervalues():
        if val is not ' ':
            stat = True
            break

    if stat:
        result = ''
        for k in changed_sites.iterkeys():
            changes = changed_sites[k]
            changed_cost = ''
            for change in changes:
                change = ' '.join(get_data_from_html(change).split('/$'))
                if change:
                    changed_cost = '; '.join([change, changed_cost])
            if changed_cost:
                line = ' '.join([k, changed_cost])
                result = '\n'.join([result, line])

        stats = SendStatistics()
        stats.post(data=result)

    return render_template('changes.html', site_names=URLS,
                           sites=changed_sites,
                           site='')


#------------------------------------------
# Method for check last result with previous
#------------------------------------------
def search_result_by_time():
    if request.method == 'POST':
        time = request.form['time']
        date = request.form['date']
        try:
            end_date = datetime.datetime.strptime(date + ' 00:00', '%m/%d/%Y %H:%M')
            start_date = end_date + datetime.timedelta(days=1)
            q = "SELECT * FROM ResultModel WHERE timestamp <= DATETIME('%s') AND timestamp >= DATETIME('%s')" % (start_date, end_date)
            results = ndb.gql(q).fetch()
        except ValueError:
            results = ''

    return render_template('list_data.html', site_names=URLS, results=results)
