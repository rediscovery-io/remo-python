class Image:
    __slots__ = ('sdk', 'id', 'name', 'dataset', 'url', 'path')

    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.dataset = kwargs.get('dataset')
        self.path = kwargs.get('path')

    def __str__(self):
        return 'Image: {} - {}'.format(self.id, self.name)

    def __repr__(self):
        return self.__str__()
