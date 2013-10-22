import functools

from film_common.utils.redis_intf import acquire_lock
import logging
logger = logging.getLogger(__name__)

def single_instance_task(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        try:
            with acquire_lock("single_instance_task_%s_%r_%r" % (func.__name__, args, kw)):
                func(*args, **kw)
        except acquire_lock.AlreadyAcquired, e:
            logging.warning("lock for %r already acquired" % func.__name__)
            pass
    return wrapper

