import falcon


class Heartbeat(object):
    """Handler class for `heartbeat` route"""
    def on_post(self, req, resp):
        """Returns empty response"""
        resp.context['result'] = None
        resp.status = falcon.HTTP_204
