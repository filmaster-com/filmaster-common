from celery.decorators import task

@task
def dump_cache():
    from film_common.utils import cache_in_redis
    cache_in_redis._RedisJusticeKeeper.dump_cache()
