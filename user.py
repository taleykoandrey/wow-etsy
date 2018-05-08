import requests
import json
import traceback
import time

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

    et.info(msg='send request to ' + url)
    r = requests.get(url, auth=etsy_auth.oauth)
    remain = r.headers['X-RateLimit-Remaining']
    et.info(msg='X-RATE-REMAINING: ' + remain)
    print("REMAIN:", remain)
    if r.status_code > 400:
        et.error(r.content)
        et.error("FINISH get_user_id_or_login_name")
        return False

    try:
        data = json.loads(r.content.decode('utf-8'))
    except:
        et.error(traceback.format_exc())
        return False

    login_name = False
    try:
        int(user_id)
    except ValueError:
        login_name = True

    et.info("FINISH get_user_id_or_login_name")
    time.sleep(0.1)

    # only 1 result in list of results.
    if login_name:
        try:
            user_id = data['results'][0]['user_id']
        except IndexError:
            user_id = 0  # anonymus
        return user_id
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


def connect_users_db(user_name):
    """
    connect users.
    :param user_name: user, whose connected user should be written to db.
    """
    et.info("START write_connected_users_to_db")

    # get id of user_name by login name.
    user_id = get_user_id_or_login_name(user_name)

    # retrieve set of users, whom user_name connected.
    to_users_id = get_connected_users(user_id)

    for to_user_id in to_users_id:
        connect_user_db(user_id, to_user_id)

    et.info("FINISH write_connected_users_to_db")


def circle_users_db(user_name):
    """
    circle users.
    :param user_name: user, for whom users connected him should be written to db.
    """
    et.info("START connect_users_to_db")

    # get id of user_name by login name.
    user_id = get_user_id_or_login_name(user_name)

    # retrieve set of users id, who connected user_name.
    to_users = get_circles_containing_user(user_id)

    for to_user_id in to_users:
        connect_user_db(to_user_id, user_id)  # reverse order of args!

    et.info("FINISH connect_users_to_db")


def connect_user_db(user_id, to_user_id):
    """
    add pair of connected users into db.
    :param user_id:
    :param to_user_id:
    """
    sql = "SELECT add_connected_user(%s, %s)"
    cur = cnn.cursor()
    try:
        cur.execute(sql, (user_id, to_user_id))
        cnn.commit()
        et.info("pair of user ({0} - {1}) add".format(user_id, to_user_id))
    except psycopg2.IntegrityError:
        cnn.rollback()
        et.info("pair of user ({0},{1}) already exists".format(user_id, to_user_id))


def unconnect_user_db(user_id, to_user_id):
    """
    add pair of connected users into db.
    :param user_id:
    :param to_user_id:
    """
    sql = "SELECT set_user_unconnect(%s, %s)"
    cur = cnn.cursor()
    try:
        cur.execute(sql, (user_id, to_user_id))
        cnn.commit()
        et.info("pair of user ({0} - {1}) unconnected".format(user_id, to_user_id))
    except:
        cnn.rollback()
        et.error("error during unconnect_user_db\n" + traceback.format_exc())


def get_users_to_unconnect_db(user_id):
    """
    get to_users_id who didn't connect user_name.
    :param user_id: user, for whom users should be unconnected.
    """
    et.info("START get_users_to_unconnect_db")

    cur = cnn.cursor()
    users = {}

    sql = "SELECT get_users_to_unconnect(%s)"
    try:
        cur.execute(sql, (user_id, ))
        users = cur.fetchall()
        cnn.commit()
    except:
        cnn.rollback()

    et.info("FINISH get_users_to_unconnect_db")
    return users


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

    # todo: bugs with utf-8 (with user names)
    et.info(msg=''.join((str(r.status_code), r.content.decode("utf-8"))))
    et.info(msg="FINISH connect_user();")


def unconnect_user(user_id, to_user_id):
    """
    /users/:user_id/circles/:to_user_id
    Removes a user (to_user_id) from the logged in user's (user_id) circle
    :param: user_id: user for whom to_user_id would be unconnected,
    :param: to_user_id: user, who would be unconnected from user_id.
    """
    et.info(msg="START unconnect_user();")

    url_suffix = ''.join(('/users/', str(user_id), '/circles/', str(to_user_id)))
    url = etsy_auth.url + url_suffix

    et.info(msg='send request to ' + url)

    r = requests.delete(url, auth=etsy_auth.oauth)

    # todo: bugs with utf-8
    et.info(msg=''.join((str(r.status_code), r.content.decode('cp1251'))))
    et.info(msg="FINISH unconnect_user();")


def unconnect_users_of_user(user_name):
    """
    :param: user_id: user for whom to_user_id would be unconnected,
    """
    et.info(msg="START unconnect_users();")

    user_id = get_user_id_or_login_name(user_name)

    # retrieve users who should be unconnected.
    to_users_id = get_users_to_unconnect_db(user_id)

    for to_user_id in to_users_id:
        unconnect_user(user_id, to_user_id[0])
        unconnect_user_db(user_id, to_user_id[0])

    et.info(msg="FINISH unconnect_users();")


def was_user_connected_to_user(user_id, to_user_id):
    """
    check if to_user_id was ever connected to user_id.
    :param user_id:
    :param to_user_id:
    :return boolean.
    """
    et.info(msg="START was_user_connected_to_user();")
    sql = "SELECT was_user_connected_to_user(%s, %s)"
    cur = cnn.cursor()
    res = False

    try:
        cur.execute(sql, (user_id, to_user_id))
        res = cur.fetchone()[0]
        cnn.commit()
    except:
        cnn.rollback()
        et.error("error during was_user_connected_to_user\n" + traceback.format_exc())
    et.info(msg="FINISH was_user_connected_to_user();")
    return res


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
    unconnect_users_of_user('Lylyspecial')


if __name__ == '__main__':
    main()
