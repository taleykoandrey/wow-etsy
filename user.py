import requests
import json

from etsy_logger import elogger as et
from etsy_auth import etsy_auth


def get_user_id_by_login_name(user_id):
    """
    Retrieves a User by id.
    /users/:user_id
    :param user_id: login_name (only!) of user.
    :return: id of user
    """

    url_suffix = ''.join(('/users/', user_id))
    url = etsy_auth.url + url_suffix

    et.info(msg='send request to ' + url)
    r = requests.get(url, auth=etsy_auth.oauth)
    data = json.loads(r.content.decode('utf-8'))
    # only 1 result in list of results.
    return data['results'][0]['user_id']


def get_user_login_name_by_user_id(user_id):
    """
    Retrieves a User by id.
    /users/:user_id
    :param user_id: id (only!) of user.
    :return: login_name of user
    """

    url_suffix = ''.join(('/users/', user_id))
    url = etsy_auth.url + url_suffix

    et.info(msg='send request to ' + url)
    r = requests.get(url, auth=etsy_auth.oauth)
    data = json.loads(r.content.decode('utf-8'))
    # only 1 result in list of results.
    return data['results'][0]['login_name']


def get_circles_containing_user(user_id):
    """
    /users/:user_id/connected_users
    Returns a set of users who have circled this user.
    :return: set.
    """
    circled_users = set()

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
            circled_users.add(user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    return circled_users


def get_connected_users(user_id):
    """
    /users/:user_id/connected_users

    :return: set of connected users_id.
    """
    et.info(msg='START get_connected_users: ')

    connected_users = set()
    connected_user_id = set()

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
            connected_users.add(connected_user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    et.info(msg='FINISH get_connected_users: ')

    return connected_users


def get_connected_users_name(user_id):
    """
    retrieve names of connected users.
    /users/:user_id/connected_users

    :param: user_id: id of user for whom connected users're retrieved.
    :return: set of connected users.
    """
    et.info(msg='START get_connected_users: ')

    connected_users = set()
    connected_user_name = set()

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
                connected_user_name = res['login_name']
            except KeyError:  # hidden user.
                pass
            connected_users.add(connected_user_name)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    et.info(msg='FINISH get_connected_users: ')

    return connected_users


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


def main():

    print(get_user_login_name_by_user_id('88483150'))


if __name__ == '__main__':
    main()
