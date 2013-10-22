from django.conf import settings

class BaseApp(object):
    """
    base class for extendable django applications
    """

    name = 'base_app'

    AUTH_USER_PASS = None

    def __init__(self, **kw):
        for (k, v) in kw.items():
            if not hasattr(self.__class__, k):
                raise Exception("invalid keyword parameter: %r" % k)
            setattr(self, k, v)

        for cls in reversed(self.__class__.mro()[:-1]):
            vars(self).update(getattr(settings, "%s_CONFIG" % getattr(cls, 'name').upper(), {}))

    @property
    def urls(self):
        return self.get_urls(), self._app_name(), self.name

    @classmethod
    def _app_name(cls):
        """
        returns application namespace
        https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces
        """
        names = [c.name for c in reversed(cls.mro()[:-1]) if c.name != BaseApp.name]
        if not names:
            raise Exception("cls.name must be redefined in subclass of BaseApp")
        return names[0]

