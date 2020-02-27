class Image:
    __slots__ = ('sdk', 'id', 'name', 'dataset_id', 'url', 'path', 'size', 'width', 'height', 'upload_date')

    def __init__(
        self,
        sdk,
        id: int = None,
        name: str = None,
        dataset_id: int = None,
        path: str = None,
        url: str = None,
        size: int = None,
        width: int = None,
        height: int = None,
        upload_date: str = None,
    ):
        self.sdk = sdk
        self.id = id
        self.name = name
        self.dataset_id = dataset_id
        self.path = path
        self.url = url
        self.size = size
        self.width = width
        self.height = height
        self.upload_date = upload_date

    # save_to(path)
    # get_annotation_sets()
    # get_annotation(annotation_set_id)
    # add_annotation(Annotation)
    # view()
    # annotate(annotation_set_id)

    def __str__(self):
        return 'Image: {} - {}'.format(self.id, self.name)

    def __repr__(self):
        return self.__str__()

    def get_content(self):
        """
        Retrieves image file content

        Returns:
            image binary data
        """
        if not self.url:
            print('ERROR: image url is not set')
            return

        return self.sdk.get_image_content(self.url)
