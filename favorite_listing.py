import requests
import json

from etsy_logger import elogger as et
from etsy_auth import etsy_auth


class FavoriteListing:

    @staticmethod
    def find_all_listing_favored_by(listing_id):
        """
        Retrieves a set of FavoriteListing objects associated to a Listing.
        NB: no pagination, so generator can't be used.
        /listings/:listing_id/favored-by
        :param listing_id: id of listing.
        :return: set of user who added listing to favorite.
        """
        users = []

        url_suffix = ''.join(('/listings/', listing_id, '/favored-by'))
        url = etsy_auth.url + url_suffix
        et.info(msg='send request to ' + url)

        r = requests.get(url, auth=etsy_auth.oauth)
        data = json.loads(r.content.decode('utf-8'))

        for res in data['results']:
            try:
                users.append(res['user_id'])
            except KeyError:  # hidden info.
                pass

        return set(users)

    @staticmethod
    def create_user_favorite_listing(user_id, listing_id):
        """
        creates a new favorite user for a user.
        /users/:user_id/favorites/listings/:listing_id

        :param: listing_id: listing which would be favorited.
        :param: user_id: user who would be favorited.
        """

        # https://openapi.etsy.com/v2/users/andreytaleyko/favorites/listings/488799483?api_key=gbhgd9nyejoj3b3x4ezz055x

        url_suffix = ''.join(('/users/', user_id, '/favorites/listings/', str(listing_id)))
        url = etsy_auth.url + url_suffix

        et.info(msg='send request to ' + url)

        r = requests.post(url, auth=etsy_auth.oauth)


