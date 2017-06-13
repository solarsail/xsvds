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



        resp.status = falcon.HTTP_200
        resp.context['result'] = {
            vm_id: {
                'rdp_ip': '192.168.1.52',
                'rdp_port': 5903
            }
        }

