import configparser
import requests

from requests_oauthlib import OAuth1


def get_key_url():
    """
    get url and key from config file.
    :return:
    key: token
    url: main url
    """
    config_parser = configparser.ConfigParser()
    config_parser.read('D:/projects/wow-etsy/etsy.conf')
    url = config_parser.get('API', 'URI')
    key = config_parser.get('API', 'KEYSTRING')
    key_secret = config_parser.get('API', 'SHARED-SECRET')
    resource_owner_key = config_parser.get('API', 'RESOURCE-OWNER-KEY')
    resource_owner_secret = config_parser.get('API', 'RESOURCE-OWNER-SECRET')
    user = config_parser.get('USER', 'name')

    return url, key, key_secret, resource_owner_key, \
           resource_owner_secret, user


class EtsyAuth:
    def __init__(self):
        self.url, self.client_key, self.client_secret, \
            self.resource_owner_key, self.resource_owner_secret,\
            self.user = get_key_url()

        self.oauth = OAuth1(self.client_key,
                            client_secret=self.client_secret,
                            resource_owner_key=self.resource_owner_key,
                            resource_owner_secret=self.resource_owner_secret)


etsy_auth = EtsyAuth()


def get_token():
    # http://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html
    from urllib.parse import parse_qs

    """
    1. Obtain a request token which will identify you (the client) in the next
    step. At this stage you will only need your client key and secret.
    """
    url = 'https://openapi.etsy.com/v2/oauth/request_token?scope=favorites_rw%20profile_w%20feedback_r'
    client_key, client_secret = get_key_url()[1:3]

    oauth = OAuth1(client_key, client_secret=client_secret)
    r = requests.post(url, auth=oauth)
    credentials = parse_qs(r.content.decode('utf-8'))
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    """
    2. Obtain authorization from the user (resource owner) to access their
    protected resources (images, tweets, etc.).
    This is commonly done by redirecting the user to a specific url to which
    you add the request token as a query parameter.
    Note that not all services will give you a verifier even if they should.
    Also the oauth_token given here will be the same as the one in the
    previous step.
    """
    login_url = credentials.get('login_url')[0]
    print('Please go here and authorize ', login_url)
    verifier = input('Please input the verifier \n')

    """ 3. Obtain an access token from the OAuth provider.
    Save this token as it can be re-used later.
    In this step we will re-use most of the credentials obtained uptil this point.
    """
    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)
    access_token_url = 'https://openapi.etsy.com/v2/oauth/access_token'
    r = requests.post(url=access_token_url, auth=oauth)
    credentials = parse_qs(r.content.decode('utf-8'))
    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]
    print(r.content)

    return resource_owner_key, resource_owner_secret


def main():
    get_token()


if __name__ == '__main__':
    main()
