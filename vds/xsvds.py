import logging
import logging.config
import falcon

from vds import api, logconf
from vds.interface import xapi, ldap_ as ldap
from vds.utils import RequireJSON, JSONTranslator, RequireAuth, Logger, handle_vds_exception
from vds.exceptions import VDSError, HTTPServerError, HTTPAuthError, VDSError
from vds.config import CONF


logging.config.dictConfig(logconf.conf_dict)
log = logging.getLogger('vds.main')

# build http server
app = falcon.API(middleware=[RequireJSON(), JSONTranslator(), Logger(), RequireAuth()])
app.add_error_handler(VDSError, handle_vds_exception)

conf_xs = CONF['xs']
conf_ldap = CONF['ldap']
try:
    # initialize xenserver & ldap
    ldap.init(conf_ldap['ip'], conf_ldap['port'], domain=conf_ldap['domain'])
    log.info("LDAP initalized.")
    xapi.init(conf_xs['ip'], conf_xs['username'], conf_xs['password'])
    log.info("XAPI initalized.")
    # normal routes
    app.add_route("/v1/login", api.login)
    app.add_route("/v1/conn", api.connect)
except VDSError as e:
    log.exception(e)
    # failsafe routes
    app.add_route("/v1/login", api.failsafe)
    app.add_route("/v1/conn", api.failsafe)




