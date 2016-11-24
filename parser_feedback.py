import requests
import configparser
import lxml.html

from etsy_logger import elogger as et
from user import get_user_id_or_login_name

config_parser = configparser.ConfigParser()
config_parser.read('etsy.conf')
url_shop = config_parser.get('URL', 'url-shop')
users_feedback_list = config_parser.get('LOG', 'users-feedback-list')


def gen_pages_for_shop(shop_id):
    """
    generate urls for parsing users, who left feedback.
    https://www.etsy.com/ru/shop/OrgonitePyramid/reviews?ref=pagination&page=2'

    :param shop_id: name of shop
    :yield: urls.
    """
    for i in range(1, 50):
        uri = ''.join((url_shop, shop_id,
                       '/reviews?ref=pagination&page=', str(i)))
        print(uri)
        yield uri


def get_users_from_xml(root):
    """
    parse xml node and extract users.

    :param root: node of xml
    :return: set of users id.
    """
    xml_users_id = set()
    # often user left more than 1 feedback, so it's useful to save user names
    # to reduce number of requests.
    xml_users_name = set()

    tree = lxml.html.fromstring(root)

    for elem in tree.find_class('circle float-right'):
        user_name = elem.get('alt')  # get name of user
        if user_name not in xml_users_name:
            xml_users_name.add(user_name)
            user_id = get_user_id_or_login_name(user_name)  # get id by name.
            if user_id:  # valid user name.
                xml_users_id.add(user_id)

    return xml_users_id


def get_users_left_feedback_to_shop(shop_id):
    """
    get users who left feedback to shop.

    :param shop_id: name of shop
    :return: users: set of user
    """
    et.info(msg='START get_users_left_feedback_to_shop: ' + shop_id)

    users = set()
    for url in gen_pages_for_shop(shop_id):
        et.info(msg='send request to ' + url)
        r = requests.get(url)
        data = r.content.decode('utf-8')
        new_users = get_users_from_xml(data)
        # if new users (not yet appended to result set) exist.
        if len(new_users - users) > 0:
            # users.update(new_users)  # append new users
            yield new_users
        else:  # suppose that in this case no new users exist.
            break

    et.info(msg='FINISH  get_users_left_feedback_to_shop: ' + shop_id)


def main():
    users = get_users_left_feedback_to_shop('OrgonitePyramid')


if __name__ == '__main__':
    main()
