import logging
import falcon

from vds import token
from vds.interface import xapi, ldap_ as ldap


log = logging.getLogger(__name__)

class Login(object):
    """Handler class for `login` route"""
    def on_post(self, req, resp):
        """handle POST request and generate response"""
        data = req.context['doc']
        username = data['username']
        password = data['password']

        user_info = ldap.auth(username, password) # raises on failure
        log.info("User [{}] logging in. ({})".format(username, user_info))

        t = token.issue(username)
        log.info("Token issued for user [{}].".format(username))

        vms = xapi.current_session().get_vms_by_user(username)
        log.info("VM info retrieved for user [{}], {} VM(s) in total.".format(username, len(vms)))

        info = {}
        for i, vm in enumerate(vms):
            log.debug("[{}] {}".format(i+1, vm))
            info[vm['uuid']] = {
                'name': vm['name'],
                'status': vm['power_state'],
                'public_ip': vm['ip'],
                'os': vm['os']['distro'] if vm['os'] else 'unknown'
            }

        resp.context['result'] = {
            'vms': info,
            'token': t
        }

        resp.status = falcon.HTTP_200

