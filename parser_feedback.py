import requests
import configparser
import lxml.html
#from fake_useragent import UserAgent
from string import whitespace
import time

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
    ?ref=pagination&page=, str(i))
    """
    for i in range(1, 2):
        uri = ''.join((url_shop, shop_id,
                       '/#reviews?ref=pagination&page=', str(i)))
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
        # remove all kin of whitespaces
        user_name = user_name.translate(dict.fromkeys(map(ord, whitespace)))
        if user_name not in xml_users_name:
            xml_users_name.add(user_name)
            user_id = get_user_id_or_login_name(user_name)  # get id by name.
            time.sleep(0.5)
            if user_id:  # valid user name.
                xml_users_id.add(user_id)

    return xml_users_id


def get_users_left_feedback_to_shop(shop_id):
    """
    generator function yield users who left feedback to shop.

    :param shop_id: name of shop
    :yield: set of users
    """
    et.info(msg='START get_users_left_feedback_to_shop: ' + shop_id)

    # users in current shop page
    new_users = set()
    # users in all searched pages
    new_users_all = set()

    for url in gen_pages_for_shop(shop_id):
        et.info(msg='send request to ' + url)
        r = requests.get(url)
        print (r.reason)
        # page not found.
        if r.status_code >=400:
            return -1

        data = r.content.decode('utf-8')
        try:
            new_users = get_users_from_xml(data)
            new_users_all =  new_users | new_users_all
        except:
            print("get_users_from_xml. can't retrieve data from xml")
            continue

    et.info(msg='FINISH  get_users_left_feedback_to_shop: ' + shop_id)
    return new_users_all



def main():
    users = get_users_left_feedback_to_shop('SunMoonandEarth')


if __name__ == '__main__':
    main()
