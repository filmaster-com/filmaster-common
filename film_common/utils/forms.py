from django import forms

class PrefixedForm(forms.Form):
    prefix = forms.CharField(widget=forms.HiddenInput)
    PREFIX = None

    @classmethod
    def get_prefix(cls):
        return '%s_prefix' % (cls.PREFIX or cls.__name__.lower())

    def add_prefix(self, field_name):
        if field_name == 'prefix':
            return self.get_prefix()
        return super(PrefixedForm, self).add_prefix(field_name)

    @classmethod
    def get_bound_forms(cls, data, **kw):
        return [cls(data, prefix=prefix, **kw) for prefix in data.getlist(cls.get_prefix())]

    @classmethod
    def get_valid_forms(cls, data, **kw):
        return [f for f in cls.get_bound_forms(data, **kw) if f.is_valid()]

    def __init__(self, *args, **kw):
        prefix = kw.pop('prefix')
        initial = kw.pop('initial', None) or {}
        assert prefix
        initial['prefix'] = prefix
        super(PrefixedForm, self).__init__(prefix=prefix, initial=initial, *args, **kw)


