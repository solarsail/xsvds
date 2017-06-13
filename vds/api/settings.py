import logging
import falcon

from vds import token


log = logging.getLogger(__name__)

class Settings(object):
    """Handler class for `settings` route"""
    def on_post(self, req, resp):
        """handle POST request and generate response"""
        data = req.context['doc']
        query = data['query']


        ret = {}
        if 'otp' in query:
            ret['otp'] = False

        resp.status = falcon.HTTP_200
        resp.context['result'] = ret

