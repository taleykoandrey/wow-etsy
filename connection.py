import configparser
import psycopg2

config_parser = configparser.ConfigParser()

config_parser.read('etsy.conf')


dbname = config_parser.get('DB', 'dbname')
user = config_parser.get('DB', 'user')
password = config_parser.get('DB', 'password')
host = config_parser.get('DB', 'host')
port = config_parser.get('DB', 'port')


# todo: handle errors.
cnn = psycopg2.connect(database=dbname,
                       user=user,
                       host=host,
                       port=port)
# shared cursor
cur = cnn.cursor()


def is_exist_user(user_id):
    cur.execute("SELECT is_exist_user(%s)", (user_id, ))
    print (cur.fetchone())


def main():
    is_exist_user('Lylyspecial')


if __name__ == '__main__':
    main()
