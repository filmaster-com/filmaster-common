import json
import datetime
import uuid
import pytz

from film_common.utils.importlib import import_object
from django.db.models.base import ModelState

def _hint(constructor, *args, **kw):
    if isinstance(kw.get('_state'), ModelState):
        # do not serialize internal state of django db models
        kw.pop('_state')
    return dict(
            __jsonclass__ = ["%s.%s" % (constructor.__module__, constructor.__name__), list(args)],
            **kw)

def type_hinter(obj, default=None):
    if hasattr(obj, '__jsonhint__'):
        c, args, attrs = obj.__jsonhint__()
        return _hint(c, *args, **attrs)
    elif isinstance(obj, datetime.datetime):
        args = list(obj.timetuple()[0:6])
        args.append(obj.microsecond)
        if obj.tzinfo:
            args.append(_hint(pytz.FixedOffset, obj.tzinfo.utcoffset(obj).seconds / 60))
        return _hint(obj.__class__, *args)
    elif isinstance(obj, datetime.date):
        return _hint(obj.__class__, *obj.timetuple()[0:3])
    elif isinstance(obj, uuid.UUID):
        return _hint(uuid.UUID, str(obj))
    elif isinstance(obj, set):
        return _hint(set, list(obj))
    if default is None:
        default = repr

    return default(obj)

def object_hook(obj):
    jc = obj.get('__jsonclass__')
    if isinstance(jc, list):
        klass = import_object(jc[0])
        if klass is not None:
            obj.pop('__jsonclass__')
            try:
                params = jc[1]
            except IndexError:
                params = []
            o = klass(*params)
            for (k, v) in obj.iteritems():
                setattr(o, k, v)
            return o
    return obj

def dumps(s, default=None, encoding='utf-8'):
    return json.dumps(s, default=lambda o: type_hinter(o, default), encoding=encoding)

def loads(s):
    return json.loads(s, object_hook=object_hook)



