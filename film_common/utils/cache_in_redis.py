import random
from django.conf import settings

from film_common.utils.redis_intf import redis
from film_common.models import RedisCacheDumps
from film_common import tasks

from recommendation_service.stats import stats
from redis import WatchError


import logging
logger = logging.getLogger(__name__)


class _RedisJusticeKeeper:
    """
    Keeps watch over fifo of objects cached in redis.
    """
    CACHE_QUEUE_KEY = 'cache_queue'
    KEYS_SET_KEY = 'cached_set'
    DELAYED_JOB_KEY = 'delayed_cache_job'
    KEY_LOCK_PREFIX = 'locked:'

    ADD_KEY_IF_NOT_ADDED_SCRIPT = """
if redis.call("sismember", KEYS[1], ARGV[1]) == 1 then
        return 0
end
redis.call("sadd", KEYS[1], ARGV[1])
redis.call("rpush", KEYS[2], ARGV[1])
return 1
    """

    INIT_SET_FROM_QUEUE = """
local a = redis.call("lrange", KEYS[2], 0, -1)
for i, v in ipairs(a) do
        redis.call("sadd", KEYS[1], v)
        redis.call("set", ARGV[1]..":"..v, '1')
end
"""

    DELETE_IF_BIG_IDDLE_SCRIPT = """
if redis.call("object", "idletime", KEYS[1]) > tonumber(ARGV[1]) then
    redis.call("del", KEYS[1])
    return 1
end
return 0
"""

    """Maximal number of objects cached in redis."""
    MAX_CACHE_SIZE = settings.REDIS_CACHE_SIZE
    MAX_CACHE_OVERFLOW = int(settings.REDIS_CACHE_SIZE * 0.05)

    """Minimal idle time of object to be removed from cache.  WARNING:
       During heavy stress it may be removed earlier.
    """
    MIN_IDLE_TIME = 60
    MAX_KEY_BUNDLE_SIZE = 500  # delayed job will request from
                            # redis key bundles of this size

    @staticmethod
    def make_set_equal_to_queue():
        redis.eval(
            _RedisJusticeKeeper.INIT_SET_FROM_QUEUE,
            2,
            _RedisJusticeKeeper.KEYS_SET_KEY,
            _RedisJusticeKeeper.CACHE_QUEUE_KEY,
            _RedisJusticeKeeper.KEY_LOCK_PREFIX
        )

    @staticmethod
    def load_to_redis(key):
        try:
            dump = _RedisJusticeKeeper.dump_from_db(key)
        except:
            return False

        try:
            redis.execute_command('restore', key, 0, dump)
            _RedisJusticeKeeper.add_to_queue(key)
            return True
        except:
            logger.info("Cannot load %s key to redis from db." % key)
        return False

    @staticmethod
    def dump_from_db(key):
        return RedisCacheDumps.objects.get(pk=key).dump

    @staticmethod
    def add_to_queue(key):
        redis_cq_key = _RedisJusticeKeeper.CACHE_QUEUE_KEY
        redis_s_key = _RedisJusticeKeeper.KEYS_SET_KEY
        delayed_job_key = _RedisJusticeKeeper.DELAYED_JOB_KEY

        if redis.eval(_RedisJusticeKeeper.ADD_KEY_IF_NOT_ADDED_SCRIPT, 2,
                redis_s_key, redis_cq_key, key):

            qu_len = redis.llen(redis_cq_key)
            max_cache = _RedisJusticeKeeper.MAX_CACHE_SIZE + \
                    _RedisJusticeKeeper.MAX_CACHE_OVERFLOW

            if qu_len > max_cache and redis.incr(delayed_job_key) < 2:
                try:
                    tasks.dump_cache.delay()
                except Exception as e:
                    redis.set(delayed_job_key, 0)
                    raise e

            if random.random() < 0.001:
                stats.gauge('tracker.cache_redis.qsize', qu_len)

    @staticmethod
    def multi_pop(pipe, set_k_key, cache_qu_key, n):
        """Returns only keys which existed in key set.
        """
        pipe.multi()
        pipe.lrange(cache_qu_key, 0, n - 1)
        pipe.ltrim(cache_qu_key, n, -1)
        popped = pipe.execute()[0]
        for el in popped:
            pipe.srem(set_k_key, el)
        rem_stat = pipe.execute()

        counter = 0
        result = []
        for key, removed in zip(popped, rem_stat):
            if removed:
                result += [key]
            else:
                counter += 1
        return result, counter

    @staticmethod
    def dump_cache():
        try:
            dj_key = _RedisJusticeKeeper.DELAYED_JOB_KEY
            min_idle = _RedisJusticeKeeper.MIN_IDLE_TIME
            cache_qu_key = _RedisJusticeKeeper.CACHE_QUEUE_KEY
            set_k_key = _RedisJusticeKeeper.KEYS_SET_KEY
            range_size = _RedisJusticeKeeper.MAX_KEY_BUNDLE_SIZE - 1
            max_cache_size = _RedisJusticeKeeper.MAX_CACHE_SIZE
            add_if_not_added = _RedisJusticeKeeper.ADD_KEY_IF_NOT_ADDED_SCRIPT
            key_lock_prefix = _RedisJusticeKeeper.KEY_LOCK_PREFIX

            multi_pop = _RedisJusticeKeeper.multi_pop
            qulen = redis.llen(cache_qu_key)
            dlen = qulen - max_cache_size
            pipe = redis.pipeline()

            first_key = None

            fail = False

            while dlen > 0 and not fail:
                keys_to_process, lost = multi_pop(pipe, set_k_key, cache_qu_key, range_size)
                dlen -= lost

                for key in keys_to_process:
                    if first_key == key:
                        fail = True
                        break

                    removed = False
                    if dlen > 0:
                        with redis.pipeline() as watch_pipe:
                            try:
                                key_lock = '%s:%s' % (key_lock_prefix, key)
                                watch_pipe.watch(key, key_lock)

                                try:
                                    idletime = redis.object('idletime', key) or 0
                                except:
                                    idletime = 0

                                if idletime > min_idle:
                                    dump = redis.execute_command('dump', key)
                                    RedisCacheDumps.create_or_update(key, dump)
                                    watch_pipe.multi()
                                    watch_pipe.delete(key)
                                    watch_pipe.delete(key_lock)
                                    watch_pipe.execute()
                                    removed = True
                            except WatchError:
                                pass
                    if not removed:
                        if first_key is None:
                            first_key = key
                        pipe.eval(add_if_not_added, 2, set_k_key, cache_qu_key, key)
                    else:
                        dlen -= 1
                pipe.execute()

            if fail:
                logger.warning("DISASTER level!!! To many recently used "
                        "objects, redis memory usage may be to big soon!")
        finally:
            redis.set(dj_key, 0)


def make_sure_is_in_redis(key):
    """It will be in redis at least for one minute.
    It will raise exception if key is not stored in redis nor database.
    """
    pipe = redis.pipeline()
    pipe.set('%s:%s' % (_RedisJusticeKeeper.KEY_LOCK_PREFIX, str(key)), 1)
    pipe.type(key)
    e = pipe.execute()
    if e[1] == 'none':  # XXX(janek): assuming redis.type(key)
                                   # resets idletime of key
        _RedisJusticeKeeper.load_to_redis(key)


def set_key_as_db_stored(key):
    _RedisJusticeKeeper.add_to_queue(key)


def number_of_cached_keys():
    return redis.llen(_RedisJusticeKeeper.CACHE_QUEUE_KEY)


def set_key_as_db_stored_if_not_exists(key):
    """Returns True if key does not exists (in redis or database),
       and False if it exists.
    """
    if not redis.exists(key) and \
            RedisCacheDumps.objects.filter(pk=key).count() == 0:
        set_key_as_db_stored(key)
        return True
    return False


def force_keys_into_redis_cache(keys):
    for key in keys:
        _RedisJusticeKeeper.add_to_queue(key)
