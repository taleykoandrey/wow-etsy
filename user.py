import requests
import json
import traceback
import psycopg2

from etsy_logger import elogger as et
from etsy_auth import etsy_auth
from connection import cnn


def get_user_id_or_login_name(user_id):
    """
    Retrieves a User by id.
    /users/:user_id
    :param user_id: login_name or id of user.
    :return: id of user, if login_name was passed,
             login_name, if id.
    """
    et.info("START get_user_id_or_login_name")
    url_suffix = ''.join(('/users/', user_id))
    url = etsy_auth.url + url_suffix

    # et.info(msg='send request to ' + url)
    r = requests.get(url, auth=etsy_auth.oauth)

    if r.status_code > 400:
        et.warning(r.content)
        et.info("FINISH get_user_id_or_login_name")
        return False

    data = json.loads(r.content.decode('utf-8'))

    login_name = False
    try:
        int(user_id)
    except ValueError:
        login_name = True

    et.info("FINISH get_user_id_or_login_name")
    # only 1 result in list of results.
    if login_name:
        return data['results'][0]['user_id']
    else:
        return data['results'][0]['login_name']


def get_circles_containing_user(user_id):
    """
    /users/:user_id/connected_users
    Returns a set of users who have circled this user.
    usually this number is less than 100.
    :param user_id: login_name or id of user.
    :return: set.
    """
    circled_users = set()

    url_suffix = ''.join(('/users/', str(user_id), '/circles'))
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
                continue
            circled_users.add(user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    return circled_users


def get_connected_users(user_id):
    """
    Retrieve connected users set of user_id.
    /users/:user_id/connected_users

    :param: user_id name or id of user.
    :return: set of connected users_id.
    """
    et.info(msg='START get_connected_users: ')

    connected_users = set()

    url_suffix = ''.join(('/users/', str(user_id), '/connected_users'))
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
                continue
            connected_users.add(connected_user_id)
        if data['pagination']['next_offset'] is None:  # last page of listings.
            break
        offset += int(payload['limit'])

    et.info(msg='FINISH get_connected_users: ')

    return connected_users


def write_connected_users_to_db(user_name):
    """
    retrieve connected user set of user_name and write all pairs to db.
    :param user_name: user, whose connected user should be written to db.
    """
    et.info("START write_connected_users_to_db")

    cur = cnn.cursor()

    # get id of user_name by login name.
    user_id = get_user_id_or_login_name(user_name)

    # retrieve set of users, whom user_name connected.
    to_users_id = get_connected_users(user_id)

    sql = "SELECT add_connected_user(%s, %s)"
    for to_user_id in to_users_id:
        try:
            cur.execute(sql, (user_id, to_user_id))
            cnn.commit()
            et.info("pair of user ({0} - {1}) add".format(user_id, to_user_id))
        except psycopg2.IntegrityError:
            cnn.rollback()
            et.info("pair of user ({0},{1}) already exists".format(user_id, to_user_id))
            continue

    et.info("FINISH write_connected_users_to_db")


def write_circled_users_to_db(user_name):
    """
    retrieve users set, who connected user_name, and write all pairs to db.
    :param user_name: user, for whom users connected him should be written to db.
    """
    et.info("START write_circled_users_to_db")

    cur = cnn.cursor()

    # get id of user_name by login name.
    user_id = get_user_id_or_login_name(user_name)

    # retrieve set of users, who connected user_name.
    to_users = get_circles_containing_user(user_id)

    sql = "SELECT add_connected_user(%s, %s)"
    for to_user_id in to_users:
        try:
            cur.execute(sql, (to_user_id, user_id))  # reverse order of args!
            cnn.commit()
            et.info("pair of user ({0} - {1}) add".format(user_id, to_user_id))
        except psycopg2.IntegrityError:
            cnn.rollback()
            et.info("pair of user ({0},{1}) already exists".format(user_id, to_user_id))
            continue

    et.info("FINISH write_circled_users_to_db")


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

    url_suffix = ''.join(('/users/', str(user_id), '/connected_users'))
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
    :param: user_id: user who connected to_user_id,
    :param: to_user_id: user, who would be connected to user_id.
    """
    et.info(msg="START connect_user();")

    url_suffix = ''.join(('/users/', str(user_id), '/connected_users'))
    url = etsy_auth.url + url_suffix
    payload = {'to_user_id': str(to_user_id)}

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
        connect_user(etsy_auth.user, to_user_id)


def main():
    write_connected_users_to_db('Lylyspecial')
    # write_circled_users_to_db('Lylyspecial')
    # print(get_user_id_or_login_name('88483150'))


if __name__ == '__main__':
    main()
