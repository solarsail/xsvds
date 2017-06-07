import json
import time

from cryptography import fernet

from vds.config import CONF
from vds.exceptions import InvalidTokenError


_key = CONF['token']['secret']
_cipher = fernet.Fernet(_key)
_delta = 86400 # one day

def issue(payload):
    """Issues a token containing provided payload."""
    now = time.time()
    data = {
        'issued_at': now,
        'expire_after': _delta,
        'payload': payload
    }

    token = _cipher.encrypt(json.dumps(data))
    return token

def verify(token):
    """Verify the token and retrieves the payload."""
    try:
        data = _cipher.decrypt(token, ttl=_delta)
    except fernet.InvalidToken:
        raise InvalidTokenError("Token corrupted.")

    try:
        data = json.loads(data)
    except ValueError:
        raise InvalidTokenError("Token payload deserialization error.")

    try:
        payload = data['payload']
    except KeyError:
        raise InvalidTokenError("Invalid token payload format.")

    return payload
