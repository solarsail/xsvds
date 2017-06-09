import logging
import ldap

from vds.exceptions import AuthError, LdapError


log = logging.getLogger(__name__)


class _defs(object):
    ldap = None
    base_dn = None
    domain = None


def init(ip, port, domain):
    """Initializes LDAP connection info.

    No connection is made at this stage.
    """
    log.info("Initializing LDAP client: ip[{}], port[{}], domain[{}]".format(ip, port, domain))
    dcs = domain.split('.')
    _defs.base_dn = ','.join(["dc={}".format(dc) for dc in dcs])
    log.debug("base_dn: {}".format(_defs.base_dn))
    _defs.ldap = ldap.initialize('ldap://{}:{}'.format(ip, port))
    _defs.ldap.set_option(ldap.OPT_REFERRALS, 0) # no idea what this does, but it is necessary
    _defs.domain = domain


def auth(username, password):
    """Authenticates the user in LDAP server."""
    ##### DEBUG #####
    #return username
    #################
    username_full = "{}@{}".format(username, _defs.domain)
    search_filter = "userPrincipalName={}".format(username_full)

    try:
        _defs.ldap.simple_bind_s(username_full, password)
        r = _defs.ldap.search_s(_defs.base_dn, ldap.SCOPE_SUBTREE, search_filter)
        _defs.ldap.unbind_s()
        return r
    except (ldap.CONNECT_ERROR, ldap.SERVER_DOWN) as e:
        raise LdapError(str(e))
    except ldap.LDAPError as e:
        _defs.ldap.unbind_s()
        raise AuthError('Authentication failed: user={}, msg={}'.format(username, e))

