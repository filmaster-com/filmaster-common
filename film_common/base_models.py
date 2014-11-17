import datetime
from django.db import models
from django.utils.timezone import now

class ChangeLogManager(models.Manager):
    SYNC_DELAY = 10
    def since(self, sync_mark=None, delay=SYNC_DELAY):
        end_time = now() - datetime.timedelta(seconds = delay)
        objects = self.get_query_set()
        objects = objects.order_by('updated_at', self.model._meta.pk.name)
        objects = objects.filter(updated_at__lt=end_time)
        objects = self.model.filter_syncable(objects)
        if sync_mark:
            objects = objects.filter(self._sync_mark_to_query(sync_mark))
        return objects

    def _sync_mark_to_query(self, sync_mark):
        t, id = sync_mark.split('|', 1)
        pk_name = self.model._meta.pk.name
        return models.Q(updated_at__gt=t)|models.Q(updated_at=t, **{'%s__gt' % pk_name: id})

    def sync_mark_for(self, obj):
        return "%s|%s" % (obj.updated_at, obj.pk)

_model_meta = type(models.Model)

class RedisSyncableMeta(_model_meta):
    """
    metaclass for RedisSyncable, maintaining registry of RedisSyncable subclasses
    """
    def __new__(meta, name, bases, attrs):
        cls = _model_meta.__new__(meta, name, bases, attrs)
        if name not in ['RedisSyncable', 'RedisSyncableModel']:
            cls._subclasses[name] = cls
        return cls

class RedisSyncable(models.Model):
    """
    Abstract base db model for all models syncable to redis.
    Subclass must define changelog_entry method.
    """
    # fields for maintaining db change log, ignored when object is saved to db
    updated_at = models.DateTimeField(auto_now=True, default=datetime.datetime.now)
    sync_source = models.CharField(max_length=16, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    change_log = ChangeLogManager()
    objects = models.Manager()

    class Meta:
        abstract = True

    __metaclass__ = RedisSyncableMeta

    # registry of all subclasses of RedisSyncableModel, updated by model metaclass
    _subclasses = {}

    @classmethod
    def filter_syncable(cls, objects):
        """
        Returns objects of this model which can be synced to redis.
        """
        return objects

    @classmethod
    def get_model_names(cls):
        return sorted(cls._subclasses.keys())

    @classmethod
    def get_model(cls, model_name):
        return cls._subclasses[model_name]

    def sync_mark(self):
        return "%s|%s" % (self.updated_at, self.pk)

    def to_changelog(self):
        """
        returns ChangeLogItemBase subclass object (serializable to changelog)
        """
        raise NotImplementedError()
