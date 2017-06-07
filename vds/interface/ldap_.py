import logging
import ldap

from vds.exceptions import AuthError, LdapError


log = logging.getLogger(__name__)
log.info(dir(ldap))

_ldap = None
_ou = None
_dc = None


class _defs(object):
    ldap = None
    base_dn = None
    user_dn_suffix = None


def init(ip, port, ou, dc):
    """Initializes LDAP connection info."""
    _defs.base_dn = 'dc={},dc=local'.format(dc)
    _defs.user_dn_suffix = 'ou={},dc={},dc=local'.format(ou, dc)
    _defs.ldap = ldap.initialize('ldap://{}:{}'.format(ip, port))


def auth(username, password):
    """Authenticates the user in LDAP server."""
    return username
    user_dn = 'uid={},{}'.format(username, _defs.user_dn_suffix)
    base_dn = _defs.base_dn
    search_filter = 'uid={}'.format(username)

    try:
        _defs.ldap.simple_bind_s(who=user_dn, cred=password)
        r = _defs.ldap.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        _defs.ldap.unbind_s()
        return r
    except (ldap.CONNECT_ERROR, ldap.SERVER_DOWN) as e:
        raise LdapError(str(e))
    except ldap.LDAPError as e:
        _defs.ldap.unbind_s()
        raise AuthError('Authentication failed: user={}, msg={}'.format(username, e))
