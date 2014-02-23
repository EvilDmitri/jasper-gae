import HTMLParser
from flask import flash, url_for
import urllib
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext.ndb import Key
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from lxml import html
import re

from application.models import ResultModel, SitesModel


TAG_RE = re.compile(r'<[^>]+>')
pClnUp = re.compile(r'\n|\t|\xa0|0xc2|\\')


def get_data_from_html(data):
    """Cleans data from tags, special symbols"""
    snippet = urllib.unquote(data)
    h = HTMLParser.HTMLParser()
    snippet = h.unescape(snippet)
    snippet = snippet.encode('utf-8')
    # Clean from tags
    snippet = TAG_RE.sub('', snippet)
    #Clean from command chars
    clean_text = str(pClnUp.sub('', snippet))

    snippet = clean_text[:1000]
    return snippet.decode('utf8', 'ignore')


def site_key(site_name):
    return ndb.Key('SitesModel', site_name)


class UltimateRewardsGrabber:
    URLS = {
        'ultimaterewardsearn.chase.com': 'http://ultimaterewardsearn.chase.com/shopping',
        'aadvantageeshopping.com': 'https://www.aadvantageeshopping.com/shopping/b____alpha.htm',
        'dividendmilesstorefront.com': 'https://www.dividendmilesstorefront.com/shopping/b____alpha.htm',
        'onlinemall.my.bestbuy.com': 'https://onlinemall.my.bestbuy.com/shopping/b____alpha.htm',
        'mileageplusshopping.com': 'https://www.mileageplusshopping.com/shopping/b____alpha.htm',
        'mileageplanshopping.com': 'https://www.mileageplanshopping.com/shopping/b____alpha.htm',
        'rapidrewardsshopping.southwest.com': 'https://rapidrewardsshopping.southwest.com/shopping/b____alpha.htm',
    }

    def __init__(self, url):
        self.url = self.URLS[url]
        self.site_name = unicode(url)

    def grab(self):
        print 'Scraping'
        website = urlfetch.fetch(self.url)
         # Save page content to string
        page = str(website.content)
        tree = html.fromstring(page)

        titles = tree.xpath('//div[@class="mn_srchListSection"]/ul/li/a[@ href="#"]')
        costs = tree.xpath('//div[@class="mn_srchListSection"]/ul/li/span')
        merchants = dict(zip(titles, costs))

        merchants_data = []
        for merchant in merchants:
            title = get_data_from_html(merchant.text)
            title = title.rstrip().lstrip()
            title = title.replace(' Details', '')

            cost = get_data_from_html(merchants[merchant].text)
            cost = cost.rstrip().lstrip()

            m = r'\t'.join([title, cost])
            merchants_data.append(m)

        merchants = r'\n'.join(str(x) for x in merchants_data)
        result = ResultModel(merchants=merchants, site_name=self.site_name)
        result.put()
        result_id = result.key.id()
        result_id = '|'.join([str(result_id), str(result.timestamp)])
        self.put_result(result_id)
        return 'OK'

    def put_result(self, result_id):
        try:
            site = SitesModel.query().filter(SitesModel.site_name == self.site_name)
            site = site.fetch()[0]
            results = '/'.join([str(site.results), str(result_id)])
            print results
            site.results = results
            site.put()
        except Exception:
            print 'ups'
            site = SitesModel(key=site_key(self.site_name), site_name=self.site_name, results=result_id)
            site.put()


if __name__ == '__main__':
    grabber = UltimateRewardsGrabber('')
    grabber.grab()
