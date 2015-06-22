from itertools import count


class PaginatedAPIIterator(object):
    def __init__(self, service_method, args=(), kwargs=None,
                 page_param='page', page_size_param='page_size',
                 page_size=100):
        self.service_method = service_method
        self.page_param = page_param
        self.page_size_param = page_size_param
        self.page_size = page_size
        self.args = args
        self.kwargs = kwargs or {}

    def __iter__(self):
        for page in self.page_ids():
            kwargs = self.kwargs.copy()
            kwargs[self.page_param] = page
            if self.page_size_param:
                kwargs[self.page_size_param] = self.page_size

            batch = self.service_method(*self.args, **kwargs)
            for result in batch:
                yield result
            if len(batch) < self.page_size:
                return

    def page_ids(self):
        return count()


class IndexedAPIIterator(PaginatedAPIIterator):
    def __init__(self, service_method, args=(), kwargs=None,
                 offset_param='offset', limit_param='limit',
                 page_size=100):
        super(IndexedAPIIterator, self).__init__(
            service_method, args, kwargs, page_param=offset_param,
            page_size_param=limit_param, page_size=page_size)

    def page_ids(self):
        return count(0, self.page_size)
