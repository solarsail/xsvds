import falcon


class Failsafe(object):
    """Handler class for failsafe routes, used on initialization failure."""
    def on_post(self, req, resp):
        """Handles POST request and generate response"""
        resp.context['result'] = {
            'err': 'Out of service'
        }

        resp.status = falcon.HTTP_500
