from .utils import build_url


class UI:
    def __init__(self, server):
        self.server = server

    def url(self, endpoint, *args, **kwargs):
        return build_url(self.server, endpoint, *args, **kwargs)

    def dataset_url(self, id=None):
        return self.url('datasets', id)

    def annotate_url(self, id):
        return self.url('annotation', id)

    def search_url(self):
        return self.url('datasets/filtered/images')

    def image_view(self, image_id, dataset_id):
        return self.url('/image/{}?datasetId={}').format(image_id, dataset_id)