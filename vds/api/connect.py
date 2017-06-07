import logging
import falcon

from vds import token
from vds.interface import xapi
from vds.exceptions import *


log = logging.getLogger(__name__)

class Connect(object):
    """Handler class for `conn` route"""
    def on_post(self, req, resp):
        """handle POST request and generate response"""
        data = req.context['doc']
        user = req.context['token']
        vm_id = data['vm_id']

        try:
            log.info("Attempt to start VM [{}] for user [{}]..".format(vm_id, user))
            xapi.current_session().start_vm(vm_id)
        except XapiOperationError as xoe:
            # starting a running VM, log and ignore
            log.info(xoe)

        info = xapi.current_session().get_vm_info(vm_id)
        log.info("Retrieved info of VM [{}].".format(vm_id))

        resp.status = falcon.HTTP_200
        resp.context['result'] = {
            vm_id: {
                'rdp_ip': info['ip'],
                'rdp_port': 3389
            }
        }

