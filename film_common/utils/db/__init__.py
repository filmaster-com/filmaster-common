class FieldChangeDetectorMixin(object):
    DETECT_CHANGE_FIELDS = ()
    def __init__(self, *args, **kw):
        super(FieldChangeDetectorMixin, self).__init__(*args, **kw)
        if self.pk:
            self._prev_values = dict((f, getattr(self, f)) for f in self.DETECT_CHANGE_FIELDS)
        else:
            self._prev_values = {}

    def has_field_changed(self, name):
        if not name in self.DETECT_CHANGE_FIELDS:
            logger.warning("field %r not present in %s.DETECT_CHANGE_FIELDS", name, self.__class__.__name__) 
            return False
        return getattr(self, name, None) != self._prev_values.get(name)

    is_field_changed = has_field_changed

    def any_field_changed(self, *names):
        return any(self.has_field_changed(name) for name in names)

    def prev_value(self, name):
        return self._prev_values.get(name)

