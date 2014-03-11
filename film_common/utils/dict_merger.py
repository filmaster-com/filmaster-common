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

    def keys(self):
        return list(set(self.a.keys()) | set(self.b.keys()))

    def __iter__(self):
        return iter(self.keys())

    def iteritems(self):
        for k in self.keys():
            v = self[k]
            if isinstance(v, DictMerger):
                v = dict(v.items())
            yield (k, v)

    def items(self):
        return list(self.iteritems())
