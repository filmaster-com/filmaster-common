from film_common.utils.redis_intf import RedisKeys
from film_common.utils.test import TestCase


class TestRedisKeys(TestCase):
    def test_it(self):
        class A:
            def __init__(self):
                self.abra = 'kadabra'
                self.czupakabra = 'siadla'
        rk = RedisKeys(('a', 'a'), ('b', '1'), ('c', '2', 1), ('d', '3', 2),
                  ('e', '4', ['abra']), ('f', '5', ['abra', 'czupakabra']),
                  ('g', '6', 1, ['abra']),
                  ('h', '7', 2, ['czupakabra', 'abra']))
        a = A()
        rk.create_redis_key_getters(a)
        self.assertTrue(a.a() == 'a')
        self.assertTrue(a.b() == '1')
        self.assertTrue(a.c(1) == '2:1')
        self.assertTrue(a.d(1, 2) == '3:1:2')
        self.assertTrue(a.e() == 'kadabra:4')
        self.assertTrue(a.f() == 'kadabra:siadla:5')
        self.assertTrue(a.g('') == 'kadabra:6:')
        self.assertTrue(a.g('padla') == 'kadabra:6:padla')
        self.assertTrue(a.h('', 'abra') == 'siadla:kadabra:7::abra')
