from .. import utils


class Dataset:

    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.annotation_sets = kwargs.get('annotation_sets')
        self.created_at = kwargs.get('created_at')
        self.license = kwargs.get('license')
        self.is_public = kwargs.get('is_public')
        self.users_shared = kwargs.get('users_shared')
        self.top3_classes = kwargs.get('top3_classes')
        self.total_classes = kwargs.get('total_classes')
        self.total_annotation_objects = kwargs.get('total_annotation_objects')

    def __str__(self):
        return 'Dataset (id={}, name={})'.format(self.id, self.name)

    def upload(self, files=[], urls=[], annotation_task=None, folder_id=None):
        return self.sdk.upload_dataset(self.id, files, urls, annotation_task, folder_id)

    def fetch(self):
        dataset = self.sdk.get_dataset(self.id)
        self.__dict__.update(dataset.__dict__)

    def browse(self):
        utils.browse(self.sdk.ui.dataset_url(self.id))

    def annotate(self):
        # TODO: select by annotation task
        if len(self.annotation_sets) > 0:
            utils.browse(self.sdk.ui.annotate_url(self.annotation_sets[0]))
        else:
            print("No annotation sets in dataset " + self.name)

    def images(self, folder_id, **kwargs):
        return self.sdk.list_dataset_contents(self.id, folder_id, **kwargs)

    def search(self, **kwargs):
        pass
