import time
import traceback

from etsy_logger import elogger as et

from user import (connect_user, get_connected_users,
                  get_connected_users_name)
from listing import find_all_shop_listings_active
from favorite_listing import find_all_listing_favored_by
from parser_feedback import get_users_left_feedback_to_shop


def find_all_users_favored_listing_in_shop(shop_id):
    """
    generator function yield a set of users.
    pagination supported by limit-offset mechanism.
    yield set of listings which contained one page, number of listing
    yielded = limit defined in payload section.
    :param shop_id: id of shop.
    :yield: set of user who added any listing of shop to favorite.
    """
    et.info(msg="START find_all_users_favored_listing_in_shop();")
    all_users = set()

    # traverse all active listings in shop.
    for listing_batch in find_all_shop_listings_active(shop_id):
        for listing in listing_batch:
            users = find_all_listing_favored_by(str(listing))
            # yield only those users, who is absent in all_users set (new users).
            yield users - all_users
            all_users = all_users | users  # add users to set.

    et.info(msg="FINISH find_all_users_favored_listing_in_shop();")
    msg = ''.join((str(len(all_users)), " users liked listings in shop ",
                   shop_id))
    et.info(msg=msg)


def connect_all_users_who_liked_shop(user_id, shop_id):
    """
    connect users who liked any listing in chosen shop.
    :param user_id: me
    :param shop_id: name of shop.
    """
    # create list of users who'e already connected.
    my_connected_users = get_connected_users(user_id)

    for batch_aimed_users in find_all_users_favored_listing_in_shop(shop_id):
        # only users who're not yet connected.
        for to_user_id in batch_aimed_users - my_connected_users:
            try:
                connect_user(user_id, str(to_user_id))
            except:
                et.error(msg=traceback.format_exc())
            time.sleep(1)
    return


def connect_all_users_who_left_feedback(user_id, shop_id):
    """
    connect users who left feedback to a shop.
    :param user_id: name of user.
    :param shop_id: name of shop.
    """
    # create set of users who'e already connected.
    my_connected_users = get_connected_users_name(user_id)

    for batch_aimed_users in get_users_left_feedback_to_shop(shop_id):
        # only users who're not yet connected.
        # todo: batch_aimed_users presents as names, though my_connected_users as id!
        for to_user_id in batch_aimed_users - my_connected_users:
            try:
                connect_user(user_id, str(to_user_id))
            except:
                et.error(msg=traceback.format_exc())
            time.sleep(0)
    return


def main():
    et.info("*"*80)
    connect_all_users_who_left_feedback('Lylyspecial', 'ChakraHealingShop')


if __name__ == '__main__':
    main()
