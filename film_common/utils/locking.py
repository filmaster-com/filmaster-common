import functools
from django.conf import settings
from film_common.utils.importlib import import_object
from hashlib import md5

import logging
logger = logging.getLogger(__name__)

def single_instance_task(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if hasattr(settings, "ACQUIRE_LOCK_PROVIDER"):
            acquire_lock = import_object(settings.ACQUIRE_LOCK_PROVIDER)
            if not acquire_lock:
                logger.warning("can't import %s, no locking", settings.ACQUIRE_LOCK_PROVIDER)
                acquire_lock = acquire_lock_dummy
        else:
            logger.warning("settings.ACQUIRE_LOCK_PROVIDER not set, no locking")
            acquire_lock = acquire_lock_dummy

        try:
            h = md5(settings.SECRET_KEY).hexdigest()
            with acquire_lock("single_instance_task_%s_%s_%r_%r" % (h, func.__name__, args, kw)):
                return func(*args, **kw)
        except acquire_lock.AlreadyAcquired, e:
            logging.warning("lock for %r already acquired" % func.__name__)
            pass
    return wrapper

class AcquireLockBase(object):
    """
        Base class for lock providers
    """

    def __init__(self, name, force=False):
        self.name = name
        self.force = force

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    class AlreadyAcquired(Exception):
        pass

class acquire_lock_dummy(AcquireLockBase):
    def __enter__(self):
        logger.debug("acquiring dummy lock for %s", self.name)
        return self

    def __exit__(self, type, value, traceback):
        logger.debug("releasing dummy lock for %s", self.name)


