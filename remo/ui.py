from .utils import build_url


class UI:
    def __init__(self, server):
        self.server = server

    def url(self, endpoint, *args, **kwargs):
        return build_url(self.server, endpoint, *args, **kwargs)

    def dataset_url(self, id=None):
        url = self.url('datasets')
        if id:
            url += str(id)
        return url

    def annotate_url(self, id):
        return self.url('annotation', id)
