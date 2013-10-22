from django.test import TestCase as DjangoTestCase, Client as DjangoClient
from django.utils import unittest

import logging
logger = logging.getLogger(__name__)

from django.db.models import signals
from django.conf import settings

from film_common.utils import cache
import sys

is_postgres = 'postgresql' in settings.DATABASES['default']['ENGINE']

class Client(DjangoClient):
    def _get_path(self, parsed):
        from django.conf import settings
        self.http_host = parsed[1] or settings.DOMAIN
        return super(Client, self)._get_path(parsed)

    def request(self, **kw):
        kw.setdefault('HTTP_HOST', self.http_host)
        return super(Client, self).request(**kw)

class TestCase(DjangoTestCase):
    client_class = Client

    def _pre_setup(self):
        from film_common.middleware import threadlocals

        self.__class__._created_models = []

        logger.info("running test %r", self.id())

        threadlocals._thread_locals.request = None
        if settings.USE_REDIS:
            from film_common.utils import redis_intf
            redis_intf.redis.flushdb()
        if hasattr(cache.cache, 'clear'):
            cache.cache.clear()
        DjangoTestCase._pre_setup(self)


from django.test.simple import DjangoTestSuiteRunner

class TestRunner(DjangoTestSuiteRunner):
    def __init__(self, verbosity=1, interactive=True, failfast=True, **kwargs):
        super(TestRunner, self).__init__(verbosity=verbosity,
                interactive=interactive, failfast=failfast, **kwargs)
        from log import set_verbosity_level
        set_verbosity_level(verbosity)

    def setup_test_environment(self, *args, **kw):
        super(TestRunner, self).setup_test_environment(*args, **kw)
        self.redis_server = None

        if settings.USE_REDIS:
            try:
                import subprocess
                self.redis_server = subprocess.Popen(['redis-server', '-'], stdin=subprocess.PIPE)
            except Exception, e:
                print e
                return
            self.redis_server.stdin.write("""
            port 63790
            loglevel warning
            """)
            settings.REDIS_HOST = 'localhost'
            settings.REDIS_PORT = 63790

            self.redis_server.stdin.close()

    def teardown_test_environment(self, *args, **kw):
        super(TestRunner, self).teardown_test_environment(*args, **kw)
        if self.redis_server:
            self.redis_server.terminate()

from nose.plugins import Plugin
import os

class Film20NoseInitializer(Plugin):
    score=99999

    def configure(self, options, conf):
        super(Film20NoseInitializer, self).configure(options, conf)
        self.enabled = True

    def begin(self):
        self.runner = TestRunner()
        self.runner.setup_test_environment()

integration_test = unittest.skipIf(not settings.INTEGRATION_TESTS, "disabled test which needs internet connection")
