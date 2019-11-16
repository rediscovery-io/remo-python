class Image:
    """
    TODO: Start using it
    WIP
    """
    id = None
    dataset = None
    path_to_image = None
    annotation_sets = []

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.dataset = kwargs.get('dataset')
        self.path_to_image = kwargs.get('path')
        # print(id, dataset,path_to_image, '\n')

