import requests
import json

from etsy_logger import elogger as et
from etsy_auth import etsy_auth


class Listing:

    @staticmethod
    def find_all_shop_listings_active(shop_id):
        """
        generator function, finds all active Listings associated with a Shop.
        pagination supported by limit-offset mechanism.
        yield set of listings which contained one page, number of listing
        yielded = limit defined in payload section.

        /shops/:shop_id/listings/active

        :param: shop_id: name or id of shop.
        """
        listings = []

        url_suffix = ''.join(('/shops/', shop_id, '/listings/active'))
        url = etsy_auth.url + url_suffix
        payload = {'limit': '50', 'offset': '0'}

        et.info(msg="START find_all_shop_listings_active();")

        offset = 0
        while 1:
            payload['offset'] = str(offset)  # refresh offset for pagination.
            et.info(msg=''.join(('send request to ', url, ' offset=', str(offset))))

            r = requests.get(url, payload, auth=etsy_auth.oauth)
            data = json.loads(r.content.decode('utf-8'))

            for res in data['results']:
                # number of appended listings = limit.
                listings.append(res['listing_id'])

            if data['pagination']['next_offset'] is None:  # last page of listings.
                et.info("next_offset is null.")
                break

            offset += int(payload['limit'])
            yield listings

        msg = ''.join(("FINISH find_all_shop_listings_active(); ",
                       str(len(listings)), " listings found"))
        et.info(msg=msg)

