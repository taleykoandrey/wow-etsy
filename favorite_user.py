import requests
import json

from etsy_logger import elogger as et
from etsy_auth import etsy_auth


def create_user_favorite_user(user_id, to_user_id):
    """
    creates a new favorite user for a user (me)
    :param: user_id: user for whom create favorite user.
    :param: to_user_id: user who would be favorited.
    """

    url_suffix = ''.join(('/users/', user_id, '/favorites/users/', to_user_id))
    url = etsy_auth.url + url_suffix

    et.info(msg='send request to ' + url)

    requests.post(url, auth=etsy_auth.oauth)


def find_all_user_favored_by(user_id):
    """
    all users who add this user to his/her favorites.
    /users/:user_id/favored-by
    :param: user_id: user id or name.
    """
    users = []

    url_suffix = ''.join(('/users/', user_id, '/favored-by'))
    url = etsy_auth.url + url_suffix
    payload = {'limit': '50', 'offset': ''}

    et.info(msg='send request to ' + url)

    offset = 0

    while 1:
        payload['offset'] = str(offset)  # refresh offset for pagination.
        r = requests.get(url, payload, auth=etsy_auth.oauth)
        data = json.loads(r.content.decode('utf-8'))

        for res in data['results']:
            try:
                user_id = res['user_id']
            except KeyError:  # hidden user.
                pass
            users.append(user_id)

        if data['pagination']['next_offset'] is None:  # last page of listings.
            break

        offset += int(payload['limit'])

    return users


def create_favorite_user_of_user(user_id):
    """
    add to favs all users who added seller to favs.
    :param: user_id: name or id of user (seller).
    """
    to_users = find_all_user_favored_by(user_id)

    for to_user in to_users:
        create_user_favorite_user(etsy_auth.user, str(to_user))