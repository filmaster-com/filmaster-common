class ListWrapper(object):
    def __init__(self, list, wrap_func = None):
        self.list = list
        self.wrap_func = wrap_func or (lambda items: items)

    def __getitem__(self, i):
        if isinstance(i, slice):
            self.list = self.list[i]
            return self
        return iter(self.wrap( (self.list[i],) )).next()

    def __len__(self):
        return len(self.list)

    def __iter__(self):
        return iter(self.wrap(self.list))

    def wrap(self, items):
        return self.wrap_func(items)

