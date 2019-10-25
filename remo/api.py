import http
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import filetype
import requests
# import psycopg2
from .domain.task import AnnotationTask
from .utils import FileResolver, build_url
from .extra_endpoints import get_dataset_info as dset_info, list_annotation_sets as list_ann_sets


class UploadStatus:

    def __init__(self, total_count: int):
        self.total_count = total_count
        self.current_count = 0
        self.start = datetime.now()
        self.reported_progress = 0

    def update(self, count: int):
        self.current_count += count

    def progress(self):
        percentage = int(self.current_count / self.total_count * 100)
        if percentage > self.reported_progress:
            elapsed = (datetime.now() - self.start).seconds + 1e-3
            avg_speed = self.current_count / elapsed
            eta = timedelta(seconds=(self.total_count - self.current_count) / avg_speed)
            print(
                'Progress {}% - {}/{} - elapsed {} - speed: {} img / s, ETA: {}'.format(percentage, self.current_count,
                                                                                        self.total_count,
                                                                                        timedelta(seconds=elapsed),
                                                                                        "%.2f" % avg_speed, eta))
        self.reported_progress = percentage


class NotAuthenticatedError(Exception):
    """ Not Authenticated run-time error. """

    def __init__(self, *args, **kwargs):
        pass


class API:
    def __init__(self, server):
        self.server = server.rstrip('/')
        self.token = None
        # self.con = psycopg2.connect(database=.., user=.., password=.., host=.., port=..)

    def url(self, endpoint, **kwargs):
        return build_url(self.server, endpoint, **kwargs)

    def is_authenticated(self):
        return self.token is not None

    def auth_header(self):
        if not self.is_authenticated():
            raise NotAuthenticatedError

        return {'Authorization': 'Token {}'.format(self.token)}

    def post(self, *args, **kwargs):
        return requests.post(*args, headers=self.auth_header(), **kwargs)

    def get(self, *args, **kwargs):

        return requests.get(*args, headers=self.auth_header(), **kwargs)

    def login(self, user_email, user_pwd):
        try:
            resp = requests.post(self.url('/api/rest-auth/login'),
                             data={"password": user_pwd, "email": user_email})
        except requests.exceptions.ConnectionError:
            print('ERROR: Failed connect to server')
            return

        if resp.status_code != http.HTTPStatus.OK:
            raise Exception(resp.json())

        self.token = resp.json().get('key')

    def create_dataset(self, name, public=False):
        return self.post(self.url('/api/dataset'),
                         json={"name": name, "is_public": public}).json()

    def upload_file(self, dataset_id, path, annotation_task=None, folder_id=None):
        name = os.path.basename(path)
        files = {'files': (name, open(path, 'rb'), filetype.guess_mime(path))}
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task.value

        url = self.url('/api/dataset/{}/upload'.format(dataset_id), folder_id=folder_id)
        return self.post(url, files=files, data=data).json()

    # TODO: fix progress to include both local files and uploads
    def upload_files(self, dataset_id: int,
                     files_to_upload: list = [],
                     annotation_task: AnnotationTask = None,
                     folder_id: int = None,
                     status: UploadStatus = None):

        files = [('files', (os.path.basename(path), open(path, 'rb'), filetype.guess_mime(path))) for path in
                 files_to_upload]
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task.value

        url = self.url('/api/dataset/{}/upload'.format(dataset_id), folder_id=folder_id)

        r = self.post(url, files=files, data=data)

        if r.status_code != http.HTTPStatus.OK:
            print('Possible Error - Response:', r.text, 'files:', files_to_upload)

        status.update(len(files))
        status.progress()
        return r.json()

    # TODO: fix progress to include both local files and uploads
    def bulk_upload_files(self, dataset_id: int, files_to_upload: list,
                          annotation_task: AnnotationTask = None,
                          folder_id: int = None):

        # files to upload
        files = FileResolver(files_to_upload, annotation_task is not None).resolve()
        groups = self.split_files_by_size(files)
        status = UploadStatus(len(files))
        with ThreadPoolExecutor(1) as ex:
            res = ex.map(lambda bulk: self.upload_files(dataset_id, bulk, annotation_task, folder_id, status),
                         groups)

        results = res
        return results

    def chunks(self, my_list, chunk_size=2000):
        groups = []
        """Yield successive n-sized chunks from l."""
        for i in range(0, len(my_list), chunk_size):
            groups.append(my_list[i:i + chunk_size])

        return groups

    def split_files_by_size(self, files: list) -> list:
        groups = []
        bulk = []
        total_size = 0
        bulk_size = 8 * 1024 * 1024
        for path in files:
            total_size += os.path.getsize(path)
            bulk.append(path)
            if total_size >= bulk_size:
                groups.append(bulk)
                bulk = []
                total_size = 0

        if len(bulk):
            groups.append(bulk)
        return groups

    def upload_local_files(self, dataset_id, local_files, annotation_task=None, folder_id=None):
        payload = {"local_files": local_files}
        if annotation_task:
            payload['annotation_task'] = annotation_task.value
        if folder_id:
            payload['folder_id'] = folder_id

        url = self.url('/api/dataset/{}/upload'.format(dataset_id))
        return self.post(url, json=payload).json()

    def upload_urls(self, dataset_id, urls, annotation_task=None, folder_id=None):
        payload = {"urls": urls}
        if annotation_task:
            payload['annotation_task'] = annotation_task.value
        if folder_id:
            payload['folder_id'] = folder_id

        url = self.url('/api/dataset/{}/upload'.format(dataset_id))
        return self.post(url, json=payload).json()

    # TODO: should return only limited information on annotation sets
    def list_annotation_sets(self, dataset_id, endpoint=None):
        url = None
        if not endpoint:
            return list_ann_sets(dataset_id)
        else:
            return self.get(url).json()
    
    def list_datasets(self, endpoint=None):
        '''
        TODO: change end point used, once we have it
        returns the name and id of datasets
        NB: we don't return an actual dataset
        '''

        url = None
        if not endpoint:
            return dset_info()
        else:
            return self.get(url).json()
        
    # MC: it's export_annotations()
    #def get_annotation_set(self, ann_set_id, endpoint=None):
    #    url = None
    #    if not endpoint:
    #        return get_ann_set(ann_set_id)
    #    else:
    #        return self.get(url).json()

    def get_annotation_statistics(self, dataset_id):
        """
        Args:
            dataset_id: int
        Returns: annotation statistics
        """
        
        url = self.url('/api/v1/ui/datasets/{}/annotation-sets'.format(dataset_id))
        return self.get(url).json()

    def get_dataset(self, id):
        url = self.url('/api/dataset/{}'.format(id))
        return self.get(url).json()

    def all_info_datasets(self, **kwargs):
        url = self.url('/api/dataset', **kwargs)
        return self.get(url).json()

    def list_dataset_contents(self, dataset_id, **kwargs):
        url = self.url('/api/v1/ui/datasets/{}/images'.format(dataset_id), **kwargs)
        return self.get(url).json()

    def list_dataset_contents_by_folder(self, dataset_id, folder_id, **kwargs):
        url = self.url('/api/user-dataset/{}/contents/{}'.format(dataset_id, folder_id), **kwargs)
        return self.get(url).json()

    def export_annotations(self, annotation_set_id, annotation_format='json'):
        """
        Args:
            annotation_set_id: int
            annotation_format: can be one of ['json', 'coco'], default='json'
        Returns: annotations
        """
        url = self.url(
            'api/v1/ui/annotation-sets/{}/export/?annotation-format={}'.format(annotation_set_id, annotation_format))
        return self.get(url).json()
