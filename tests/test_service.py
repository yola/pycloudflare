from unittest import TestCase
from urlparse import parse_qs, urlparse

from mock import Mock, patch

from pycloudflare.services import CloudFlareService


class PaginationTest(TestCase):
    def setUp(self):
        def get(url):
            params = parse_qs(urlparse(url).query)
            page = int(params['page'][0])
            page_size = int(params['per_page'][0])
            start = page * page_size
            end = start + page_size
            r = {'result': self.responses[start:end]}
            return Mock(**{'json.return_value': r})

        patcher = patch('pycloudflare.services.CloudFlareService.get',
                        side_effect=get)
        patcher.start()
        self.addCleanup(patcher.stop)

        self.cf = CloudFlareService()

    def test_one_undersized_page(self):
        self.responses = range(5)
        r = list(self.cf._iter_pages('foo', page_size=10))
        self.assertEqual(r, self.responses)

    def test_multiple_full_pages(self):
        self.responses = range(20)
        r = list(self.cf._iter_pages('foo', page_size=10))
        self.assertEqual(r, self.responses)

    def test_multiple_pages(self):
        self.responses = range(25)
        r = list(self.cf._iter_pages('foo', page_size=10))
        self.assertEqual(r, self.responses)
