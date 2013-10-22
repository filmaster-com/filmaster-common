from film_common.utils.test import TestCase
from film_common.utils.api import paginated_collection, collection
from django.test.client import RequestFactory
from django import http

class APIUtilsTestCase(TestCase):
    def test_paginated_collection(self):
        f = RequestFactory()

        r = paginated_collection(f.get('/objects/'), [])

        items = [1,2,3,4,5,6,7,8,9,10]

        r = paginated_collection(f.get('/objects/?limit=4'), items)
        self.assertEquals(r['objects'], [1,2,3,4])
        self.assertTrue(r['paginator']['next_uri'])
        self.assertFalse(r['paginator']['prev_uri'])

        r = paginated_collection(f.get('/objects/?limit=4&page=2'), items)
        self.assertEquals(r['objects'], [5,6,7,8])
        self.assertTrue(r['paginator']['next_uri'])
        self.assertTrue(r['paginator']['prev_uri'])

        r = paginated_collection(f.get('/objects/?limit=4&page=3'), items)
        self.assertEquals(r['objects'], [9,10])
        self.assertFalse(r['paginator']['next_uri'])
        self.assertTrue(r['paginator']['prev_uri'])

        self.assertRaises(http.Http404,
                paginated_collection,
                f.get('/objects/?limit=4&page=4'),
                items,
        )

    def test_collection(self):
        f = RequestFactory()
        items = [1,2,3,4,5,6,7,8,9,10] * 10

        r = collection(f.get('/objects/'), items)
        self.assertEquals(r['objects'], items)

