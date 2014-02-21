from flask import flash, url_for
from google.appengine.api import urlfetch
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from lxml import html

from application.models import MerchantModel, ResultDataModel
from lib.werkzeug.utils import redirect

BASE_URL = 'http://ultimaterewardsearn.chase.com/shopping'


class UltimateRewardsGrabber:

    def __init__(self):
        self.url = BASE_URL

    def grab(self):
        website = urlfetch.fetch(self.url)
         # Save page content to string
        page = str(website.content)
        tree = html.fromstring(page)

        divs = tree.xpath('//div[class="mn_srchListSection"]')
        merchants_data = []
        for div in divs:
            try:

                merchants = div.text().split('/$')
                for merchant in merchants:
                    merchant = merchant.split('Details ')[1]
                    title = ' '.join(merchant.split(' ')[:-2])
                    cost = merchant.split(' ')[-2]
                    print title, ' - ', cost
            except IndexError:
                pass

            print title, ' - ', cost
            merchant = MerchantModel(merchant_name=form.merchant_name.data,
                                     merchant_cost=form.merchant_cost.data
                                     )

            merchant.put()
            merchant_id = merchant.key.id()
            merchants_data.append(merchant_id)

        result = ResultDataModel(merchants=''.join(merchants_data))
        result.put()
        result_id = result.key.id()
        return result_id




if __name__ == '__main__':
    grabber = UltimateRewardsGrabber()
    grabber.grab()
