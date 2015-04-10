from .models import Settings
from django.core.cache import cache

class SettingsProxy(object):
    def __init__(self, namespace):
        self.__dict__['namespace'] = namespace

    def __setattr__(self, name, value):
        obj, created = Settings.objects.get_or_create(
            namespace=self.namespace,
            key=name,
            defaults=dict(
                value=value,
            )
        )
        if not created:
            obj.value = value
            obj.save()

        cache.set(self._cache_key(name), value)

    def __getattr__(self, name):
        key = self._cache_key(name)
        value = cache.get(key)
        if value is not None:
            return value
        try:
            value = Settings.objects.get(namespace=self.namespace, key=name).value
            cache.set(key, value)
            return value
        except Settings.DoesNotExist, e:
            raise AttributeError()

    def _cache_key(self, name):
        return "dbcache:%s:%s" % (self.namespace, name)

