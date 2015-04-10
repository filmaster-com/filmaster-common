from django.db import models
from django.db.models.signals import post_save

from django.core.cache import cache

class Settings(models.Model):
    namespace = models.CharField(max_length=16)
    key = models.CharField(max_length=64, db_index=True)
    value = models.TextField(default=None, null=True, blank=True)

    class Meta:
        unique_together = [('namespace', 'key')]
        verbose_name_plural = u'Settings'

    def __unicode__(self):
        return "%s:%s" % (self.namespace, self.key)

    @classmethod
    def get(cls, namespace, key):
        cache_key = cls._cache_key(namespace, key)
        value = cache.get(cache_key)
        if value is None:
            value = cls.objects.get(namespace=namespace, key=key).value
            cache.set(cache_key, value)
        return value

    @classmethod
    def set(cls, namespace, key, value):
        obj, created = cls.objects.get_or_create(
            namespace=namespace,
            key=key,
            defaults=dict(
                value=value,
            )
        )
        if not created:
            obj.value = value
            obj.save()

    @classmethod
    def on_post_save(cls, sender, instance, *args, **kw):
        cache_key = cls._cache_key(instance.namespace, instance.key)
        cache.set(cache_key, instance.value)

    @classmethod
    def _cache_key(cls, namespace, key):
        return "db.settings:%s:%s" % (namespace, key)

post_save.connect(Settings.on_post_save, sender=Settings)
