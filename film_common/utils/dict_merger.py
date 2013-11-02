class DictMerger(object):
    def __init__(self, a, b):
        self.a = a or {}
        self.b = b or {}

    def get(self, key, default):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        va = self.a.get(key)
        vb = self.b.get(key)

        if isinstance(va, dict) or isinstance(vb, dict):
            return DictMerger(va, vb)

        if key in self.a:
            return self.a[key]
        else:
            return self.b[key]

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

