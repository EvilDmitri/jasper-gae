import HTMLParser
from flask import flash, url_for
import urllib
from google.appengine.api import urlfetch
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from lxml import html
import re

from application.models import MerchantModel, ResultDataModel, ResultModel
from lib.werkzeug.utils import redirect

BASE_URL = 'http://ultimaterewardsearn.chase.com/shopping'

TAG_RE = re.compile(r'<[^>]+>')
pClnUp = re.compile(r'\n|\t|\xa0|0xc2|\\')


def get_data_from_html(data):
    """Cleans data from tags, special symbols"""
    snippet = urllib.unquote(data)
    h = HTMLParser.HTMLParser()
    snippet = h.unescape(snippet)
    s = snippet[3:]
    snippet = s.encode('utf-8')
    # Clean from tags
    snippet = TAG_RE.sub('', snippet)
    #Clean from command chars
    clean_text = str(pClnUp.sub('', snippet))

    snippet = clean_text[:1000]
    return snippet.decode('utf8', 'ignore')


class UltimateRewardsGrabber:

    def __init__(self):
        self.url = BASE_URL

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
            title = merchant.text.rstrip().lstrip()
            title = title.replace(' Details', '')
            cost = merchants[merchant].text.rstrip().lstrip()
            cost = cost.split('p')[0].rstrip().lstrip()
            # merchant = MerchantModel(merchant_name=title,
            #                          merchant_cost=int(cost)
            #                          )
            # merchant.put()
            # merchant_id = merchant.key.id()
            # merchants_data.append(merchant_id)
            m = r'\t'.join([title, cost])
            merchants_data.append(m)

        merchants = r'\n'.join(str(x) for x in merchants_data)
        print merchants
        result = ResultModel(merchants=merchants, site_name=BASE_URL)
        result.put()
        result_id = result.key.id()

        return 'OK'




if __name__ == '__main__':
    grabber = UltimateRewardsGrabber()
    grabber.grab()
