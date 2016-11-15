import requests
import json

from etsy_logger import elogger as et
from etsy_auth import etsy_auth


def get_circles_containing_user(user_id):
    """
    /users/:user_id/connected_users
    Returns a list of users who have circled this user.
    :return: list.
    """
    circled_users = []

    url_suffix = ''.join(('/users/', user_id, '/circles'))
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
            circled_users.append(user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    return circled_users


def get_connected_users(user_id):
    """
    /users/:user_id/connected_users
    Returns a list of users that are in this user's cricle.
    :return: set of connected users.
    """
    et.info(msg='START get_connected_users: ')

    connected_users = []

    url_suffix = ''.join(('/users/', user_id, '/connected_users'))
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
                connected_user_id = res['user_id']
            except KeyError:  # hidden user.
                pass
            connected_users.append(connected_user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    et.info(msg='FINISH get_connected_users: ')

    return set(connected_users)


def get_connected_users_name(user_id):
    """
    /users/:user_id/connected_users
    Returns a list of users that are in this user's cricle.
    :return: set of connected users.
    """
    et.info(msg='START get_connected_users: ')

    connected_users = []

    url_suffix = ''.join(('/users/', user_id, '/connected_users'))
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
                connected_user_id = res['login_name']
            except KeyError:  # hidden user.
                pass
            connected_users.append(connected_user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    et.info(msg='FINISH get_connected_users: ')

    return set(connected_users)


def connect_user(user_id, to_user_id):
    """
    /users/:user_id/connected_users
    Adds user (to_user_id) to the user's (user_id) circle.
    :param: user_id: user who would be favored.
    """
    et.info(msg="START connect_user();")

    url_suffix = ''.join(('/users/', user_id, '/connected_users'))
    url = etsy_auth.url + url_suffix
    payload = {'to_user_id': to_user_id}

    et.info(msg='send request to ' + url)

    r = requests.post(url, payload, auth=etsy_auth.oauth)
    # todo: bugs with utf-8
    et.info(msg=''.join((str(r.status_code), r.content.decode('cp1251'))))
    et.info(msg="FINISH connect_user();")


def create_circle_users_of_user(user_id):
    """
    add to circle users who added seller to their circle.
    :param: user_id: name or id of user (seller), whose circled user
    we want to connect.
    """

    circled_users = get_circles_containing_user(user_id)

    for to_user_id in circled_users:
        print(to_user_id)
        connect_user(etsy_auth.user, to_user_id)