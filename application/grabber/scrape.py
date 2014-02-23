import HTMLParser
from flask import flash, url_for
import urllib, urllib2, Cookie

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


class URLOpener:
    def __init__(self):
        self.cookie = Cookie.SimpleCookie()

    def open(self, url, data=None):
        if data is None:
            method = urlfetch.GET
        else:
            method = urlfetch.POST

        while url is not None:
            response = urlfetch.fetch(url=url,
                                      payload=data,
                                      method=method,
                                      headers=self._getHeaders(self.cookie),
                                      allow_truncated=False,
                                      follow_redirects=False,
                                      deadline=10
            )
            data = None  # Next request will be a get, so no need to send the data again.
            method = urlfetch.GET
            self.cookie.load(response.headers.get('set-cookie', ''))  # Load the cookies from the response
            url = response.headers.get('location')

        return response

    def _getHeaders(self, cookie):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.2) Gecko/20090729 Firefox/3.5.2 (.NET CLR 3.5.30729)',
            'Cookie': self._makeCookieHeader(cookie)
        }
        return headers

    def _makeCookieHeader(self, cookie):
        cookieHeader = ""
        for value in cookie.values():
            cookieHeader += "%s=%s; " % (value.key, value.value)
        return cookieHeader


class Grabber():
    def __init__(self, url):
        self.site_name = unicode(url)

    @staticmethod
    def update_site_results(result_id, site_name):
        try:
            site = SitesModel.query().filter(SitesModel.site_name == site_name)
            site = site.fetch()[0]
            results = '/'.join([str(site.results), str(result_id)])
            site.results = results
            site.put()
        except Exception:
            site = SitesModel(key=site_key(site_name), site_name=site_name, results=result_id)
            site.put()

    def save_result(self, merchants_data):
        """Accept list with strings"""
        merchants = r'\n'.join(str(x) for x in merchants_data)
        result = ResultModel(merchants=merchants, site_name=self.site_name)
        result.put()
        result_id = result.key.id()
        result_id = '|'.join([str(result_id), str(result.timestamp)])
        self.update_site_results(result_id=result_id, site_name=self.site_name)
        return result_id


class XmlGrabber(Grabber):
    URLS = {
        'discover.com': 'https://www.discover.com/credit-cards/cashback-bonus/xml/ShopD_Public_CBB_Partners.xml?',
    }

    def __init__(self, url):
        Grabber.__init__(self, url)
        self.url = self.URLS[url]

    def grab(self):
        print 'Scraping xml'
        opener = URLOpener()
        website = opener.open(self.url)
        # Save page content to string
        page = str(website.content)
        tree = html.fromstring(page)

        merchants_data = []
        lines = tree.xpath('//pd')
        for line in lines:
            title = line.attrib['p']
            cost = ''.join([line.attrib['cbb'] + '% Cashback'])

            m = r'\t'.join([title, cost])
            merchants_data.append(m)

        result_id = self.save_result(merchants_data)
        return result_id




class UltimateRewardsGrabber(Grabber):
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
        Grabber.__init__(self, url)
        self.url = self.URLS[url]

    def grab(self):
        print 'Scraping'
        opener = URLOpener()
        website = opener.open(self.url)
        # Save page content to string
        page = str(website.content)
        tree = html.fromstring(page)

        titles = tree.xpath('//div[@class="mn_srchListSection"]/ul/li/a[@ href="#"]')
        costs = tree.xpath('//div[@class="mn_srchListSection"]/ul/li/span')
        merchants = dict(zip(titles, costs))

        merchants_data = []
        for merchant in merchants:
            title = get_data_from_html(merchant.text)
            title = title
            title = title.replace(' Details', '')

            cost = get_data_from_html(merchants[merchant].text)
            cost = cost

            m = r'\t'.join([title, cost])
            merchants_data.append(m)

        result_id = self.save_result(merchants_data)
        return result_id


if __name__ == '__main__':
    grabber = UltimateRewardsGrabber('')
    grabber.grab()
