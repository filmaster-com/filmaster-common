from film_common.utils.test import TestCase

from film_common.utils import cache_in_redis
from film_common.utils.redis_intf import redis


class CacheInRedisTest(TestCase):
    @staticmethod
    def nth_key(n):
        return 'keykeykey%d' % n

    @staticmethod
    def hset_keys():
        return ['keykey%d' % x for x in xrange(1000)]

    def prepare_keys(self, n):
        self.keys = []

        for x in xrange(n):
            key = self.nth_key(x)
            self.keys += [key]

            if x % 10 == 3:
                for hkey in self.hset_keys():
                    redis.hset(key, hkey, key)
            else:
                redis.set(key, key)

    @staticmethod
    def n_redis_keys():
        return redis.info()['db0']['keys']

    def test_it(self):
        self.prepare_keys(100)
        cache_in_redis._RedisJusticeKeeper.MAX_CACHE_SIZE = 20
        cache_in_redis._RedisJusticeKeeper.MAX_CACHE_OVERFLOW = 5
        cache_in_redis._RedisJusticeKeeper.MIN_IDLE_TIME = -1
        self.assertTrue(self.n_redis_keys() == 100)

        for x in xrange(26):
            cache_in_redis.set_key_as_db_stored(self.keys[x])
            cache_in_redis.make_sure_is_in_redis(self.keys[x])

        self.assertTrue(self.n_redis_keys() == 114 + 3)
        self.assertTrue(cache_in_redis.number_of_cached_keys() == 20)

        for x in xrange(26, 50):
            cache_in_redis.set_key_as_db_stored(self.keys[x])
            cache_in_redis.make_sure_is_in_redis(self.keys[x])

        self.assertTrue(cache_in_redis.number_of_cached_keys() >= 20 and
                        cache_in_redis.number_of_cached_keys() < 26)

        self.assertTrue(self.n_redis_keys() ==
                103 - 50 + 2 * cache_in_redis.number_of_cached_keys())

        for x in xrange(50):
            key = self.nth_key(x)
            cache_in_redis.make_sure_is_in_redis(key)

            if x % 10 == 3:
                for hkey in self.hset_keys():
                    self.assertTrue(redis.hget(key, hkey) == key)
            else:
                self.assertTrue(redis.get(key) == key)

            self.assertTrue(self.n_redis_keys() == 103 - 50 +
                    2 * cache_in_redis.number_of_cached_keys())
