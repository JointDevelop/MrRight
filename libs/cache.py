from redis import Redis as _Redis
from pickle import dumps, loads, UnpicklingError

from common.config import REDIS


class Redis(_Redis):
    def set(self, name, value, ex=None, px=None, nx=False, xx=False, keepttl=False):
        """
        Set the value at key ``name`` to ``value``
        ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds.
        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.
        ``nx`` if set to True, set the value at key ``name`` to ``value`` only
               if it does not exist.
        ``xx`` if set to True, set the value at key ``name`` to ``value`` only
               if it already exists.
        ``keepttl`` if True, retain the time to live associated with the key.
                (Available since Redis 6.0)
        """
        value = dumps(value)
        return super(Redis, self).set(name, value, ex, px, nx, xx, keepttl)

    def get(self, name,default=None):
        """
        Return the value at key ``name``, or None if the key doesn't exist
        """
        value = super(Redis, self).get(name)
        if not value:
            return default
        else:
            try:
                return loads(value)
            except UnpicklingError:
                return value


rds = Redis(**REDIS)
