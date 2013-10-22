from django.conf import settings
from django.core.mail import mail_admins

import requests as requests_module

class BaseAlert(object):
    _instance_cnt = 0

    def __init__(self):
        self.__class__._instance_cnt += 1
        self.order = self._instance_cnt
        self._requests_session = None

    def check_and_notify(self, requests_session=None):
        self.requests = requests_session or requests_module
        if not self.check():
            self.notify()

    def notify(self):
        mail_admins('[Alert] %s' % self.get_title(), self.get_message())

    def check(self):
        raise NotImplemented

    def get_title(self):
        raise NotImplemented

    def get_message(self):
        raise NotImplemented

    def __nonzero__(self):
        return self.check()

    def __unicode__(self):
        return self.get_title()

class GraphiteAlert(BaseAlert):
    title_template = None
    target_template = None

    def __init__(self, target=None, min=float('-inf'), max=float('inf'), title=None, **kw):
        super(GraphiteAlert, self).__init__()
        self.min = min
        self.max = max
        self.value = None
        self.target = target or (self.target_template and self.target_template % kw)
        self.title = title or (self.title_template and self.title_template % kw)

    def get_value(self):
        data = self._get_stats(self.target)
        dp = data and data[0].get('datapoints', ()) or ()
        values = [i[0] for i in dp if i[0] is not None]
        return values and values[-1] or None

    def check(self):
        self.value = self.get_value()
        return self.value is not None and (self.min < self.value < self.max)

    def get_title(self):
        return self.title or self.target

    def get_message(self):
        t = self.get_title()
        return u"%s: %s" % (self.get_title(), self.value)

    def _get_stats(self, target, from_str='-5min', to_str='now'):
        params = {'format': 'json',
                  'target': target,
                  'from': from_str,
                  'to': to_str}
        response = self.requests.get('%s/render' % settings.GRAPHITE_URL.rstrip('/'),
                                params=params, verify=False)
        response.raise_for_status()
        return response.json()

class FreeMemAlert(GraphiteAlert):
    target_template = 'sumSeries(servers.%(host)s.memory.Cached,servers.%(host)s.memory.MemFree)'
    title_template = '%(host)s free memory'

class DiskSpaceAlert(GraphiteAlert):
    target_template = 'servers.%(host)s.diskspace.root.byte_avail'
    title_template = '%(host)s diskspace'

class LoadAvgAlert(GraphiteAlert):
    target_template = 'servers.%(host)s.loadavg.05'
    title_template = '%(host)s load'

