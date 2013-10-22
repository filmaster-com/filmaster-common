from django.db import models
import base64
import cPickle as pickle


class RedisCacheDumps(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    _dump = models.TextField(db_column='dump', blank=True)

    def set_data(self, dump):
        self._dump = base64.encodestring(dump)

    def get_data(self):
        return base64.decodestring(self._dump)

    dump = property(get_data, set_data)

    @staticmethod
    def create_or_update(key, dump):
        o = RedisCacheDumps(key=key, dump=dump)
        o.save()


def save_pickled_to_db(db_key, sth_to_be_pickled):
    dump = pickle.dumps(sth_to_be_pickled, protocol=pickle.HIGHEST_PROTOCOL)
    RedisCacheDumps.create_or_update(db_key, dump)


def load_pickled_from_db(db_key):
    try:
        dump = RedisCacheDumps.objects.get(pk=db_key)
        return pickle.loads(dump.dump)
    except RedisCacheDumps.DoesNotExist:
        return None
