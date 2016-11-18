import requests
import json

from etsy_logger import elogger as et
from etsy_auth import etsy_auth


class Feedback:

    @staticmethod
    def find_all_user_feedback_as_subject(user_id):
        """
        Retrieves a set of Feedback objects associated to a User.
        /users/:user_id/feedback/as-subject
        """
        feedbacks = []

        url_suffix = ''.join(('/users/', user_id, '/feedback/as-subject'))
        url = etsy_auth.url + url_suffix
        payload = {'limit': '50', 'offset': ''}

        et.info(msg='send request to ' + url)

        offset = 0
        while 1:
            payload['offset'] = str(offset)  # refresh offset for pagination.
            r = requests.get(url, auth=etsy_auth.oauth)
            print(r.content, r.headers)
            data = json.loads(r.content.decode('utf-8'))
            for res in data['results']:
                try:
                    user_id = res['user_id']
                except KeyError:  # hidden user.
                    pass
                feedbacks.append(user_id)
            if data['pagination']['next_offset'] is None:  # last page of listings.
                break
            offset += int(payload['limit'])

        return feedbacks