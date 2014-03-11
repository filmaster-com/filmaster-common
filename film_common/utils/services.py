from django.conf import settings

class ServiceProvider(object):

    class InvalidServiceConfig(Exception):
        pass

    def __call__(self, *args, **kwargs):
        cfg = getattr(settings, self.SETTINGS_CONFIG_KEY, {}).copy()
        cfg.update(kwargs)

        if not 'cls' in cfg:
            return self._rpc_proxy(*args, **cfg)

        cls_path = cfg.pop('cls')

        if isinstance(cls_path, basestring):
            from film_common.utils.importlib import import_object
            cls = import_object(cls_path)
            if cls is None:
                raise self.InvalidServiceConfig("cannot resolve service class: %s" % cls_path)
        else:
            cls = cls_path

        return cls(*args, **cfg)

    def _rpc_proxy(self, url=None, **kw):
        import cgi
        from urllib import urlencode

        if url is None:
            url = getattr(settings, self.SETTINGS_DEFAULT_RPC_URL_KEY)

        if '?' in url:
            url, qs = url.split('?')
        else:
            qs = ''

        qs = dict(cgi.parse_qsl(qs))
        qs.update(kw)

        if qs:
            url = url + '?' + urlencode(qs)
        return self.create_rpc_proxy(url)

    def create_rpc_proxy(self, url):
        from film_common.utils import jsonrpc
        return jsonrpc.Server(url)

