from itertools import count


class PaginatedAPIIterator(object):
    page_param = 'page'
    page_size_param = 'page_size'
    page_size = 100

    def __init__(self, service_method, args=(), kwargs=None):
        self.service_method = service_method
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
    def page_ids(self):
        return count(0, self.page_size)
