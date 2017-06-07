from vds.api.login import Login
from vds.api.connect import Connect
from vds.api.failsafe import Failsafe

login = Login()
connect = Connect()
failsafe = Failsafe()

__all__ = [login, connect, failsafe]

