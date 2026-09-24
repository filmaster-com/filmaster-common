#-------------------------------------------------------------------------------
# Filmaster - a social web network and recommendation engine
# Copyright (c) 2009 Filmaster (Borys Musielak, Adam Zielinski).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
import datetime
from django.utils.functional import SimpleLazyObject
from django.utils.encoding import smart_str
import cPickle

from django.conf import settings

import logging
logger = logging.getLogger(__name__)

import types


class RedisKeys(object):
    """This class is helper for using and generating redis keys.
    For example usage check:
        :cls:`film_common.tests.redis_keys_test.TestRedisKeys`.
    """
    def __init__(self, *keys):
        self.keys = keys

    def __call__(self, cls):
        """
        Called when RedisKeys is used as class decorator (preferred way)
        """
        self.create_redis_key_getters(cls)
        return cls

    def create_redis_key_getters(self, klass_or_instance):
        if isinstance(klass_or_instance, type):
            klass = klass_or_instance
        else:
            klass = klass_or_instance.__class__

        for key in self.keys:
            name = key[0]
            redis_name = key[1]
            d = []
            n = 0

            if len(key) > 2 and type(key[2]) == int:
                n = key[2]
            if len(key) > 2 and type(key[2]) == list:
                d = key[2]
            if len(key) > 3 and type(key[3]) == list:
                d = key[3]

            setattr(klass, name, self.create_getter(n, d, redis_name))

    def create_getter(self, n, d, redis_name):
        def fun(other_self, *args):
            key_parts = [other_self.__dict__[attr] for attr in d]
            key_parts.append(redis_name)
            assert len(args) == n
            key_parts.extend(args)
            return ':'.join(map(smart_str, key_parts))
        return fun

def remove_what_is_to_remove(to_remove_key_prefixes=None):
    if to_remove_key_prefixes is None:
        to_remove_key_prefixes = settings.REDIS_PREFIXES_TO_REMOVE

    for key_prefix in to_remove_key_prefixes:
        rks = redis.keys(key_prefix + '*')
        if rks:
            redis.delete(*rks)


def create_redis_connection():
    import redis
    unix_socket = getattr(settings, 'REDIS_UNIX_SOCKET')
    password = getattr(settings, 'REDIS_PASSWORD')
    if unix_socket:
        ret = redis.Redis(unix_socket_path=unix_socket, db=settings.REDIS_DB, password=password)
    else:
        ret = redis.Redis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB, password=password)

    settings.MAX_REDIS_MEMORY_USAGE = ret.config_get('maxmemory')
    return ret


redis = SimpleLazyObject(create_redis_connection)


def _rating_key(film_id=None, actor_id=None, director_id=None, type=1):
    key = ('type', str(type))
    if film_id:
        key += ('film', str(film_id))
    if actor_id:
        key += ('actor', str(actor_id))
    if director_id:
        key += ('director', str(director_id))

    return ':'.join(key)


def rate(user_id, rating, film_id=None, actor_id=None, director_id=None, type=1, overwrite=True, check_if_exists=False):
    user_key = "user:%s:ratings" % user_id

    key = _rating_key(film_id, actor_id, director_id, type)

    assert user_id

    if not overwrite or check_if_exists:
        exists = redis.hget("ratings:%s" % key, user_id) is not None
        if not overwrite and exists:
            return exists
    else:
        exists = None

    with redis.pipeline() as pipe:
        if rating:
            if type == 1 and film_id:
                pipe.hset(user_key, film_id, rating)
                pipe.sadd("users", user_id)
            pipe.hset("ratings:%s" % key, user_id, rating)
            pipe.set("user:%s:rating:%s" % (user_id, key), rating)
        else:
            if type == 1:
                pipe.hdel(user_key, film_id)
            pipe.hdel("ratings:%s" % key, user_id)
            pipe.delete("user:%s:rating:%s" % (user_id, key))
        pipe.execute()
    return exists


def get_rating(user_id, film_id=None, actor_id=None, director_id=None, type=1):
    key = _rating_key(film_id, actor_id, director_id, type)
    value = redis.hget("ratings:%s" % key, user_id)
    if value is not None:
        value = int(value)
    return value


def get_user_ids(min_ratings=1):
    ids = set()
    user_ids = redis.smembers('users')
    for user_id in user_ids:
        if redis.hlen('user:%s:ratings' % user_id) >= min_ratings:
            ids.add(int(user_id))
    return ids


def get_user_ratings(user_id):
    if not user_id:
        return dict()
    user_key = "user:%s:ratings" % user_id
    return dict((int(id), int(r)) for (id, r) in redis.hgetall(user_key).items())


def get_user_ratings_count(user_id):
    if not user_id:
        return 0
    user_key = "user:%s:ratings" % user_id
    return redis.hlen(user_key)


def get_rated_films(user_id):
    if not user_id:
        return set()
    user_key = "user:%s:ratings" % user_id
    return set(int(id) for id in redis.hkeys(user_key))


def get_film_ratings(film_id):
    return get_ratings(film_id=film_id, type=1)


def get_ratings(film_id=None, actor_id=None, director_id=None, type=1):
    key = "ratings:%s" % _rating_key(film_id, actor_id, director_id, type)
    return dict((int(id), int(r)) for (id, r) in redis.hgetall(key).items())


SEEN_EXPIRES_IN_DAYS = 30


def mark_films_as_seen(user, film_ids):
    user_id = str(user.id or user.username)
    key = 'user:%s:seen:%s' % (user_id, datetime.date.today())
    redis.sadd(key, *film_ids)
    redis.expire(key, SEEN_EXPIRES_IN_DAYS * 24 * 3600)


def get_seen_films(user):
    user_id = str(user.id or user.username)
    key_prefix = "user:%s:seen" % user_id
    keys = ["%s:%s" % (key_prefix, (datetime.date.today() - datetime.timedelta(days=i))) for i in range(SEEN_EXPIRES_IN_DAYS)]
    return set(int(id) for id in redis.sunion(keys))


def get_ids_with_features(key_prefix):
    return redis.smembers("%s:ids" % key_prefix)


def reset_ids_with_features(key_prefix):
    return redis.delete("%s:ids" % key_prefix)


def add_to_set(key_prefix, id, data_set):
    key = key_with_prefix(key_prefix, id)
    redis.sadd(key, *data_set)


def add_to_dict(key_prefix, id, data_dict):
    if data_dict:
        key = key_with_prefix(key_prefix, id)
        redis.hmset(key, data_dict)


def get_string_set(key_prefix, id):
    key = key_with_prefix(key_prefix, id)
    return redis.smembers(key)


def get_int_set(key_prefix, id):
    key = key_with_prefix(key_prefix, id)
    return set([int(el) for el in redis.smembers(key)])


def get_int_dict(key_prefix, id):
    return get_dict(key_prefix, id)


def get_dict(key_prefix, id, key_type=int, val_type=int):
    key = key_with_prefix(key_prefix, id)
    return dict([(key_type(a), val_type(b)) for (a, b) in redis.hgetall(key).items()])


def reset_features(key_prefix, id, type=None):
    # TODO - type support
    key = key_with_prefix(key_prefix, id)
    redis.delete(key)


def set_features(key_prefix, id, features):
    # TODO - type support
    key = key_with_prefix(key_prefix, id)
    redis.set(key, cPickle.dumps(features))
    redis.sadd("%s:ids" % key_prefix, id)


def get_features(key_prefix, id, type=None):
    # TODO - type support
    # assert key_prefix.startswith('cache_user')
    key = key_with_prefix(key_prefix, id)
    features = redis.get(key)
    if not features:
        return dict()
    return cPickle.loads(features)


def get_many_features(key_prefix, ids, type=None):
    keys = [key_with_prefix(key_prefix, id) for id in ids]
    features = redis.mget(*keys)
    return dict((k, cPickle.loads(v)) for (k, v) in zip(ids, features) if v)


def add_as_pickle_to_redis(key_prefix, id, data, redis=redis):
    """Dumps data by using cPickle and saves it in redis.
       Returns size in bytes of pickled data.
    """
    dump = cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL)
    key = key_with_prefix(key_prefix, id)
    redis.set(key, dump)
    return len(dump)


def multiple_add_as_pickle_to_redis(key_prefix, ids, datas, redis=redis):
    """Same as add_as_pickle_to_redis, but it can save multiple
       data objects at one call.
    """
    def mapper(x):
        key = key_with_prefix(key_prefix, x[0])
        dump = cPickle.dumps(x[1], cPickle.HIGHEST_PROTOCOL)
        return key, dump

    mapping = dict(map(mapper, zip(ids, datas)))
    redis.mset(mapping)


def get_unpickled_from_redis(key_prefix, id, redis=redis):
    """Loads data from redis, and unpickles it.  If redis don't contains
       given key ('key_prefix:id') this function will return None.
    """
    key = key_with_prefix(key_prefix, id)
    dump = redis.get(key)
    if not dump:
        return None
    return cPickle.loads(dump)


def multiple_get_unpickled_from_redis(key_prefix, ids, redis=redis):
    """As get_unpickled_from_redis but it can load multiple pickles at one
       call.
    """
    keys = map(lambda id: key_with_prefix(key_prefix, id), ids)
    dumps = keys and redis.mget(keys) or ()
    results = map(lambda dump: None if not dump else cPickle.loads(dump),
                  dumps)
    return results


def key_with_prefix(prefix, key):
    return '%s:%s' % (prefix, key)


def _fix1_remove_undeleted_ratings(update=False):
    total = 0
    err = 0
    keys = redis.keys("ratings:*")
    all_keys = set(redis.keys("user:*:rating:*"))
    for key in keys:
        ratings = redis.hgetall(key)
        with redis.pipeline() as pipe:
            for user_id, value in ratings.items():
                rkey = key[8:]
                k = "user:%s:rating:%s" % (user_id, rkey)
                if not k in all_keys:
                    # remove keys not removed due to bug in rate func
                    pipe.hdel(key, user_id)
                    print key
                    err += 1
                else:
                    total += 1
            if update:
                pipe.execute()
    print total, len(all_keys), err

from film_common.utils.locking import AcquireLockBase

class acquire_lock(AcquireLockBase):
    def __enter__(self):
        if not redis.setnx('lock_%s' % self.name, 'locked') and not self.force:
            raise self.AlreadyAcquired('lock %s already acquired' % self.name)
        return self

    def __exit__(self, type, value, traceback):
        redis.delete('lock_%s' % self.name)
