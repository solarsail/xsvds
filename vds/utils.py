import random
import string
import json
import logging
import falcon

from vds import token
from vds.exceptions import *


log = logging.getLogger(__name__)


class Logger(object):
    """Middleware class for request/response logging."""
    def process_request(self, req, resp):
        """Logs incoming requests.

        Args:
            see falcon documentation.
        """
        if req.path == '/v1/heartbeat':
            return

        rid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)) # a random request id
        req.context['_rid'] = rid
        log.info("**REQUEST**  [{}] from: [{}], route: {}, content: {}".format(rid, req.remote_addr, req.path, req.context['doc']))

    def process_response(self, req, resp, resource, req_succeeded):
        """Logs responses.

        Args:
            see falcon documentation.
        """
        if req.path == '/v1/heartbeat':
            return

        # `resp.body` is not translated from `context` yet if no exception is raised.
        content = resp.context['result'] if req_succeeded else resp.body
        log.info("**RESPONSE** [{}] content: {}, succeeded: {}".format(
            req.context['_rid'], content, req_succeeded))


class RequireAuth(object):
    """Middleware class for token validation."""

    exempts = ['login', 'settings']

    def process_resource(self, req, resp, resource, params):
        """Validates the token and insert the payload into the request.

        Args:
            see falcon documentation.
        """
        for item in RequireAuth.exempts:
            if req.path.endswith(item):
                return

        try:
            t = req.context['doc']['token'].encode('utf-8') # convert unicode to str
            payload = token.verify(t)
            req.context['token'] = payload
        except KeyError:
            raise InvalidTokenError


class RequireJSON(object):
    """Middleware class for request content validation."""

    def process_request(self, req, resp):
        """Validates the request content.

        Args:
            see falcon documentation.
        """
        if req.method in ('POST', 'PUT'):
            if not req.content_type or 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'This API only supports requests encoded as JSON.')


class JSONTranslator(object):
    """Middleware class for converting request content into JSON and insert into request object."""

    def process_request(self, req, resp):
        """Translates the request content into JSON and insert into the request.

        Args:
            see falcon documentation.
        """
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes from the request body.
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(falcon.HTTP_753,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect or not encoded as '
                                   'UTF-8.')

    def process_response(self, req, resp, resource):
        """Translates the response content into JSON and makes the response body.

        Args:
            see falcon documentation.
        """
        if 'result' not in resp.context:
            return

        resp.body = json.dumps(resp.context['result'])

def handle_vds_exception(ex, req, resp, params):
    """Handle all VDSError exceptions that are not caught.

    Convert VDSErrors to HTTPErrors which are used by falcon to produce responses.

    Raises:
        HTTPAuthError: if user failed to authenticate or token is invalid.
        HTTPServerError: if backend server failed to perform certain operations.
    """
    log.warning(ex)
    if type(ex) == AuthError:
        raise HTTPAuthError("Invalid username or password")
    elif type(ex) == InvalidTokenError:
        raise HTTPAuthError("Invalid token")
    elif type(ex) == XapiError:
        raise HTTPServerError("Virtual desktop server is unable to execute certain operations")
    elif type(ex) == LdapError:
        raise HTTPServerError("Cannot connect to LDAP server")
    else:
        log.exception(ex)
        raise HTTPServerError("Unexpected error: {}".format(ex.message))
