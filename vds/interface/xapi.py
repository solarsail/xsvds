import logging

from vds.driver import XenAPI
from vds.exceptions import *


log = logging.getLogger(__name__)

def need_auth(func):
    def wrapper(self, *args, **kwargs):
        """Checks if the client is authenticated and ready for use.

        Raises:
            XapiAuthError: if the client is yet authenticated.
        """
        if self.ready:
            return func(self, *args, **kwargs)
        else:
            raise XapiAuthError("XAPI client not authenticated yet.")
    return wrapper


_session = None

def init(ip, username, password):
    global _session
    _session = XapiClient(ip)
    _session.login(username, password)


def current_session():
    global _session
    return _session


class XapiClient(object):
    """Wrapper class of a xapi session.

    Attributes:
        _user_field (str): the field in `other_config` to store the associated user.
    """

    # the username to which a VM is associated
    _user_field = 'XenCenter.CustomFields.owner'

    def __init__(self, ip):
        """Build the client with XenServer IP address.

        Args:
            ip (str): XenServer IP.
        """
        self.url = "http://{}".format(ip)
        self.session = XenAPI.Session(self.url)
        self.ready = False

    def login(self, username, password):
        """Authenticate with XAPI server.

        This should be done before all other operations.

        Args:
            username (str): XenServer root username.
            password (str): XenServer root password.

        Raises:
            XapiAuthError: if the username or password is incorrect.
            XapiError: when encountered unexpect XAPI errors.
        """
        try:
            self.session.xenapi.login_with_password(username, password)
            self.ready = True
        except XenAPI.Failure as e:
            if 'SESSION_AUTHENTICATION_FAILED' in e.details:
                raise XapiAuthError("XenServer authenticaion failed.")
            else:
                raise XapiError("Unexpected XAPI error: {}".format(e))
        except IOError as e:
            raise XapiError("Unable to connect to XAPI server: {}".format(e))


    def _get_vm_info(self, vm_ref):
        vm = self.session.xenapi.VM.get_record(vm_ref)
        vgm_ref = self.session.xenapi.VM.get_guest_metrics(vm_ref)

        vm_info = {}

        uuid = vm['uuid']
        vm_name = vm['name_label']
        power_state = vm['power_state']

        vm_info = {
            'power_state': power_state,
            'name': vm_name,
            'ip': None,
            'os': {},
            'uuid': uuid,
        }

        if vgm_ref != 'OpaqueRef:NULL':
            vgm = self.session.xenapi.VM_guest_metrics.get_record(vgm_ref)
            ip = vgm['networks']['0/ip'] if '0/ip' in vgm['networks'].keys() else ''
            os = vgm['os_version']
            vm_info['ip'] = ip
            vm_info['os'] = os

        return vm_info

    @need_auth
    def get_vms_by_user(self, username):
        """Retrieve all VMs associated with the specific virtual desktop user.

        Args:
            username (str): name of a virtual desktop user.

        Returns:
            list: A list of VMs associated with the user.

            A VM is provided as a dict, e.g.

                {
                    'uuid': VM uuid,
                    'name': VM name label,
                    'power_state': Running / Halted (others are not supposed to be seen),
                    'ip': VM IP address (may be empty if xentools not functioning properly),
                    'os': {
                        'distro': centos, winxp, etc.,
                        'major': major version,
                        'minor': minor version,
                        'name': full name of OS
                    } (may be empty if xentools not functioning properly)
                }
        """
        user_vms = []

        all_vm_ref = self.session.xenapi.VM.get_all()
        for vm_ref in all_vm_ref:
            other_config = self.session.xenapi.VM.get_other_config(vm_ref)
            if XapiClient._user_field not in other_config.keys():
                continue

            if other_config[XapiClient._user_field] == username:
                user_vm = self._get_vm_info(vm_ref)
                user_vms.append(user_vm)

        return user_vms

    @need_auth
    def get_vm_info(self, vm_uuid):
        """Retrieve VM info.

        Args:
            vm_uuid (str): VM uuid.

        Returns:
            VM information, see `get_vms_by_user()`

        Raises:
            XapiError: when encountered unexpect XAPI errors.
        """
        try:
            vm_ref = self.session.xenapi.VM.get_by_uuid(vm_uuid)
            vm_info = self._get_vm_info(vm_ref)
            return vm_info
        except XAPI.Failure as e:
            raise XapiError("Unexpected XAPI error: {}".format(e))

    @need_auth
    def start_vm(self, vm_uuid):
        """Start the VM.

        Only effective if the VM is in Halted state.

        Args:
            vm_uuid (str): VM uuid.

        Raises:
            XapiOperationError: if VM is not powered off.
            XapiError: when encountered unexpect XAPI errors.
        """
        try:
            vm_ref = self.session.xenapi.VM.get_by_uuid(vm_uuid)
            self.session.xenapi.VM.start(vm_ref, False, True)
        except XenAPI.Failure as e:
            if 'VM_BAD_POWER_STATE' in e.details:
                raise XapiOperationError("VM [{}] is not in 'Halted' state."
                        " Start operation is ignored.".format(vm_uuid))
            else:
                raise XapiError("Unexpected XAPI error: {}".format(e))

    @need_auth
    def shutdown_vm(self, vm_uuid):
        """Shutdown the VM.

        Attempts to first clean shutdown a VM and if it should fail
        then perform a hard shutdown on it.

        Args:
            vm_uuid (str): VM uuid.

        Raises:
            XapiOperationError: if VM is not running.
            XapiError: when encountered unexpect XAPI errors.
        """
        try:
            vm_ref = self.session.xenapi.VM.get_by_uuid(vm_uuid)
            self.session.xenapi.VM.shutdown(vm_ref)
        except XenAPI.Failure as e:
            if 'VM_BAD_POWER_STATE' in e.details:
                raise XapiOperationError("VM [{}] is not in appropriate power states for shutdown."
                        " Shutdown operation is ignored.".format(vm_uuid))
            else:
                raise XapiError("Unexpected XAPI error: {}".format(e))

