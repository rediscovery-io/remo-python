from .api import API
from .domain.dataset import Dataset
from .ui import UI


class SDK:
    def __init__(self, server, user_email=None, user_password=None):
        self.api = API(server)
        self.ui = UI(server)
        if user_email and user_password:
            self.api.login(user_email, user_password)

    def login(self, user_email, user_pwd):
        self.api.login(user_email, user_pwd)

    def create_dataset(self, name, public=False) -> Dataset:
        result = self.api.create_dataset(name, public)
        return Dataset(self, **result)

    def get_dataset(self, id) -> Dataset:
        result = self.api.get_dataset(id)
        return Dataset(self, **result)

    def list_datasets(self, **kwargs) -> [Dataset]:
        result = self.api.list_datasets(**kwargs)
        datasets = []
        for dataset_json in result['results']:
            datasets.append(Dataset(self, **dataset_json))
        return datasets

    def upload_dataset(self, dataset_id, files=[], urls=[], annotation_task=None, folder_id=None):
        result = {}
        if len(files):
            files_upload_result = self.api.upload_files(dataset_id, files, annotation_task, folder_id)
            result['files_upload_result'] = files_upload_result

        if len(urls):
            urls_upload_result = self.api.upload_urls(dataset_id, urls, annotation_task, folder_id)
            result['urls_upload_result'] = urls_upload_result

        return result

    def list_dataset_contents(self, id, folder_id, **kwargs):
        result = self.api.list_dataset_contents(id, folder_id, **kwargs)
        # print('Total count:', result.get('count'))
        print('Next:', result.get('next'))
        images = []
        for entry in result.get('results', []):
            img = entry.get('image', {})
            name = img.get('name')
            images.append(name)

        return images