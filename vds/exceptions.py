import falcon


class VDSError(Exception):
    """Base error class."""


class AuthError(VDSError):
    """User authentication failure."""


class XapiError(VDSError):
    """XAPI invocation failure."""


class XapiAuthError(XapiError):
    """XAPI client authentication failure."""


class XapiOperationError(XapiError):
    """VM operation failure."""


class InvalidTokenError(VDSError):
    """Token corrupted or invalid."""


class LdapError(VDSError):
    """Ldap connection/query error."""


class VDSHTTPError(falcon.HTTPError):
    """Base class for custom falcon exceptions."""
    def __init__(self, status, msg):
        super(VDSHTTPError, self).__init__(status)
        self.message = msg

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj['err'] = self.message
        return obj


class HTTPServerError(VDSHTTPError):
    """Unable to service due to backend server errors."""
    def __init__(self, msg):
        super(HTTPServerError, self).__init__(falcon.HTTP_500, msg)



class HTTPAuthError(VDSHTTPError):
    """Unable to service due to auth errors."""
    def __init__(self, msg):
        super(HTTPAuthError, self).__init__(falcon.HTTP_403, msg)

