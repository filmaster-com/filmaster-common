from .models import Settings

class SettingsProxy(object):
    def __init__(self, namespace):
        self.__dict__['namespace'] = namespace

    def __setattr__(self, key, value):
        Settings.set(self.namespace, key, value)

    def __getattr__(self, name):
        try:
            return Settings.get(self.namespace, name)
        except Settings.DoesNotExist, e:
            raise AttributeError()

