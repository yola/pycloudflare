from itertools import count


class PaginatedAPIIterator(object):
    page_param = 'page'
    page_size_param = 'page_size'
    page_size = 100
    pagination_type = 'page'

    def __init__(self, service_method, args=(), kwargs=None):
        self.service_method = service_method
        self.args = args
        self.kwargs = (kwargs or {}).copy()

    def __iter__(self):
        for page in self.page_ids():
            kwargs = self.kwargs
            kwargs[self.page_param] = page
            kwargs[self.page_size_param] = self.page_size

            batch = self.service_method(*self.args, **kwargs)
            for result in batch:
                yield result
            if len(batch) < self.page_size:
                return

    def page_ids(self):
        if self.pagination_type == 'page':
            return count()
        if self.pagination_type == 'item':
            return count(0, self.page_size)
        raise ValueError('Unknown pagination_type')
