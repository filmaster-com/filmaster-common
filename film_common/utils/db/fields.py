import json

from django.db import models
from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError

# http://djangosnippets.org/comments/cr/15/1478/#c2282
class JSONField(models.Field):
    """JSONField is a textfield that contains JSON-serialized objects"""

     # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "TextField"

    def get_prep_value(self, value):
        if isinstance(value, basestring) or value is None:
            return value
        return smart_unicode(value)

    def to_python(self, value):
        """Convert from JSON string to python object after we load it from the DB"""
        if not isinstance(value, basestring):
            return value
        if not value:
            return None
        try:
            value = json.loads(value)
        except Exception, e:
            raise ValidationError('Invalid JSON: %s' % e)
        self.is_value_valid(value)
        return value

    def is_value_valid(self, value):
        """subclass may redefine this method to accept only some value types"""
        return True

    def get_db_prep_save(self, value, **kw):
        """Convert our JSON object to a string before we save"""
        assert self.is_value_valid(value)
        value = json.dumps(value, cls=DjangoJSONEncoder) if value is not None else None
        return super(JSONField, self).get_db_prep_save(value, **kw)

    def formfield(self, **kw):
        defaults = {'widget': _JSONWidget, 'validators': [self.to_python]}
        defaults.update(kw)
        return super(JSONField, self).formfield(**defaults)

class DictField(JSONField):
    """DictField is a textfield that contains JSON-serialized dictionaries."""

    def __init__(self, *args, **kwargs):
        super(DictField, self).__init__(*args, **kwargs)
        if not self.has_default():
            self.default = self._DEFAULT

    def is_value_valid(self, value):
        if value is None or isinstance(value, dict):
            return True
        raise ValidationError("this is not dict instance")

    def get_db_prep_save(self, value, **kw):
        if value == self._DEFAULT:
            return value
        return super(DictField, self).get_db_prep_save(value, **kw)

    _DEFAULT = u"{}"

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["film_common\.utils\.db\.fields\.JSONField$"])
    add_introspection_rules([], ["film_common\.utils\.db\.fields\.DictField$"])
except ImportError, e:
    pass

class _JSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None, **kw):
        if value is None:
            value = ''
        elif not isinstance(value, basestring):
            value = json.dumps(value, cls=DjangoJSONEncoder, sort_keys=True, indent=4)
        attrs = attrs or {}
        attrs['cols'] = 100
        attrs['rows'] = 25
        return super(_JSONWidget, self).render(name, value, attrs=attrs, **kw)

