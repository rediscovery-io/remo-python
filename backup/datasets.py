import random
import requests
from PIL import Image
from io import BytesIO
from remo.api import api


def request(url, params=None):
    return requests.request('GET', url,
                            headers={'Authorization': 'Token d7c7a2b4f9596c7532cc271d17ebc6cb24bb9df7'},
                            params=params)


def url(endpoint):
    return f'https://remo.ai/api/{endpoint}'


def params(limit=None, offset=None):
    p = {}
    if limit is not None:
        p['limit'] = limit
    if offset is not None:
        p['offset'] = offset
    return p



class image(object):
    def __init__(self, id, name, url):
        self.id = id
        self.name = name
        self.url = url
        self._data = None

    @property
    def img(self):
        if self._data is None:
            self._download()
        return self._data

    def _download(self):
        bytes = (requests.get(self.url)).content
        self._data = Image.open(BytesIO(bytes))

    def show(self):
        self.img.show()


class dataset(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.url = api.url(f'user-dataset/{id}/')

    def images(self):
        url = f'{self.url}images/'
        r = api.request(url)
        return [image(img['id'], img['name'], img['image']) for img in r.json()['results']]

    def __iter__(self):
        self.offset = 0
        self._data = self.images()
        return self

    def __next__(self):
        if self.offset >= len(self._data):
            raise StopIteration
        self.offset += 1
        return self._data[self.offset - 1]

    def batch_iter(self, batch_size):
        self._data = self.images()
        for i in range(0, len(self._data), batch_size):
            yield self._data[i:i + batch_size]

    def sample(self, n):
        self._data = self.images()
        if n >= len(self._data):
            return self._data
        indexes = random.sample(range(len(self._data)), n)
        return [self._data[i] for i in indexes]

    def download(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


def create():
    raise NotImplementedError


def list(limit=None, offset=None):
    r = api.request(api.url('dataset/'), api.params(limit, offset))
    return [dataset(d['id'], d['name']) for d in r.json()['results']]
