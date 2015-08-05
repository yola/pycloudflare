from unittest import TestCase

from pycloudflare.pagination import PaginatedAPIIterator


class PagitationTestsMixin(object):
    def test_iterate_one_undersized_page(self):
        self.responses = list(range(5))
        r = list(self.psc)
        self.assertEqual(r, self.responses)

    def test_iterate_multiple_full_pages(self):
        self.responses = list(range(20))
        r = list(self.psc)
        self.assertEqual(r, self.responses)

    def test_iterate_multiple_pages(self):
        self.responses = list(range(25))
        r = list(self.psc)
        self.assertEqual(r, self.responses)


class PagePaginationTest(TestCase, PagitationTestsMixin):
    def setUp(self):
        def get(url, page, page_size):
            start = page * page_size
            end = start + page_size
            return self.responses[start:end]

        self.psc = PaginatedAPIIterator(
            get, args=('http://example.net/',))
        self.psc.page_size = 10


class ItemPaginationTest(TestCase, PagitationTestsMixin):
    def setUp(self):
        def get(url, offset, limit):
            start = offset
            end = start + limit
            return self.responses[start:end]

        self.psc = PaginatedAPIIterator(
            get, args=('http://example.net/',))
        self.psc.page_size = 10
        self.psc.page_param = 'offset'
        self.psc.page_size_param = 'limit'
        self.psc.pagination_type = 'item'
