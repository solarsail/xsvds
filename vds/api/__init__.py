from vds.api.login import Login
from vds.api.connect import Connect
from vds.api.failsafe import Failsafe
from vds.api.heartbeat import Heartbeat

login = Login()
connect = Connect()
failsafe = Failsafe()
heartbeat = Heartbeat()

__all__ = [login, connect, failsafe, heartbeat]

