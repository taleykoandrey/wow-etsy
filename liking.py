import time
import traceback
from connection import cnn

from etsy_logger import elogger as et

from user import (connect_user, get_connected_users,
                  was_user_connected_to_user,
                  get_user_id_or_login_name, connect_user_db)
from listing import find_all_shop_listings_active
from favorite_listing import find_all_listing_favored_by
from parser_feedback import get_users_left_feedback_to_shop


sellers = ['NewMoonBeginnings']


def get_sellers():
    """
    :return:
    """
    cur = cnn.cursor()
    try:
        cur.execute("select seller_name from  sellers order by id;")
    except:
        cnn.rollback()
    res = [item[0] for item in cur.fetchall()]
    cnn.commit()
    return res


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


def connect_all_users_who_left_feedback(user_name, shop_id):
    """
    connect users who left feedback to a shop.
    :param user_id: name of user.
    :param shop_id: name of shop.
    """

    user_id = get_user_id_or_login_name(user_name)

    users = get_users_left_feedback_to_shop(shop_id)
    if users == -1:
        print("!!!")
        return
    for to_user_id in users:
        print (to_user_id)
        if was_user_connected_to_user(user_id, to_user_id):
            print("already")
            continue
        else:
            connect_user(user_id, to_user_id)
            connect_user_db(user_id, to_user_id)
            print("new")

    cur=cnn.cursor()
    cur.execute("UPDATE Sellers "
                "SET processed = CURRENT_DATE "
                "WHERE seller_name='" + shop_id + "'")
    cnn.commit()
    return


def add_seller(seller_name):
    """
    add seller to seller's table
    :param seller: name of seller
    :return:
    """
    cur = cnn.cursor()
    try:
        sql = "INSERT INTO Sellers(seller_name) VALUES(%s);"
        cur.execute(sql, (seller_name, ))
        cnn.commit()
    except:
        cnn.rollback()
        raise


def connect_fresh_users(my_name):
    """
    connect new buyers of all sellers in database.
    looking 1 or little more fresh pages with feedbacks
    :param: my_name: name of selleer for whom connect buyers
    """
    for seller in get_sellers():
        connect_all_users_who_left_feedback(my_name, seller)


def connect_all_users(my_name):
    """
    connect all buyers of all sellers in list.
    looking all pages with feedbacks, add this seller into db.
    :param: my_name: name of selleer for whom connect buyers
    """
    for seller in sellers:
        try:
            add_seller(seller)
        except:
            print ("seller already addded")
            #return
        connect_all_users_who_left_feedback(my_name, seller)


def main():
    et.info("*"*80)
    #connect_all_users('Lylyspecial')
    connect_fresh_users('Lylyspecial')


if __name__ == '__main__':
    main()
