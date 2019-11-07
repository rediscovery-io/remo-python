import http
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import filetype
import requests
from .domain.task import AnnotationTask
from .utils import FileResolver, build_url, browse


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


class BaseAPI:
    def __init__(self, server, email, password):
        self.server = server
        self.token = None
        self._login(email, password)

    def _login(self, email, password):
        try:
            resp = requests.post(self.url('/api/rest-auth/login/'),
                                 data={"password": password, "email": email})
        except requests.exceptions.ConnectionError:
            print('ERROR: Failed connect to server')
            return

        if resp.status_code != http.HTTPStatus.OK:
            raise Exception(resp.json())

        self.token = resp.json().get('key')

    def _is_authenticated(self):
        return self.token is not None

    def _auth_header(self):
        if not self._is_authenticated():
            raise NotAuthenticatedError
        return {'Authorization': 'Token {}'.format(self.token)}

    def url(self, endpoint, **kwargs):
        return build_url(self.server, endpoint, **kwargs)

    def post(self, *args, **kwargs):
        return requests.post(*args, headers=self._auth_header(), **kwargs)

    def get(self, *args, **kwargs):
        return requests.get(*args, headers=self._auth_header(), **kwargs)


class API(BaseAPI):
       
    def create_dataset(self, name, public=False):
        return self.post(self.url('/api/dataset/'),
                         json={"name": name, "is_public": public}).json()
    def upload_file(self, dataset_id, path, annotation_task=None, folder_id=None):
        name = os.path.basename(path)
        files = {'files': (name, open(path, 'rb'), filetype.guess_mime(path))}
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task.value

        url = self.url('/api/dataset/{}/upload/'.format(dataset_id), folder_id=folder_id)
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

        url = self.url('/api/dataset/{}/upload/'.format(dataset_id), folder_id=folder_id)

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

        url = self.url('/api/dataset/{}/upload/'.format(dataset_id))
        return self.post(url, json=payload).json()

    def upload_urls(self, dataset_id, urls, annotation_task=None, folder_id=None):
        payload = {"urls": urls}
        if annotation_task:
            payload['annotation_task'] = annotation_task.value
        if folder_id:
            payload['folder_id'] = folder_id

        url = self.url('/api/dataset/{}/upload'.format(dataset_id))
        return self.post(url, json=payload).json()
    
    def list_datasets(self):
        url = self.url('/api/v1/ui/datasets/')
        return self.get(url).json()
    
    def list_dataset_contents(self, dataset_id, **kwargs):
        url = self.url('/api/v1/ui/datasets/{}/images/'.format(dataset_id), **kwargs)
        return self.get(url).json()

    def list_dataset_contents_by_folder(self, dataset_id, folder_id, **kwargs):
        url = self.url('/api/user-dataset/{}/contents/{}/'.format(dataset_id, folder_id), **kwargs)
        return self.get(url).json()
    
    def get_dataset(self, id):
        url = self.url('/api/dataset/{}/'.format(id))
        return self.get(url).json()
    
    def list_annotation_sets(self, dataset_id: int):
        url = self.url('/api/v1/ui/datasets/{}/annotation-sets/'.format(dataset_id))
        return self.get(url).json()
    
    def get_annotations(self, annotation_set_id: int, annotation_format='json'):
        """
        Args:
            annotation_format: can be one of ['json', 'coco'], default='json'
        Returns: annotations
        """
        url = self.url(
            'api/v1/ui/annotation-sets/{}/export/?annotation-format={}'.format(annotation_set_id, annotation_format))
        return self.get(url).json()
    
    def export_annotation_to_csv(self, annotation_set_id: int, output_file, annotation_task):
        annotation = self.get_annotations(annotation_set_id, annotation_format='json')
        output = open(output_file,'w', newline='')
        f = csv.writer(output)
        if annotation_task.value == 'Object detection':
            header =  ['file_name', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
            f.writerow(header) 
            for item in annotation:
                annotations = item['annotations']
                for annotation in annotations:
                    classes = annotation['classes']
                    for cls in classes:
                        f.writerow([item['file_name'], cls] + list(annotation['bbox'].values()))
        elif annotation_task.value == 'Instance segmentation':
            header =  ['file_name', 'class', 'coordinates']
            f.writerow(header) 
            for item in annotation:
                annotations = item['annotations']
                for annotation in annotations:
                    classes = annotation['classes']
                    for cls in classes:
                        segments = ' '.join(str(v) for d in annotation['segments'] for k, v in d.items())
                        f.writerow([item['file_name'], cls, segments])
        else:
            # TODO: classification task 
            # MC: currently there is a bug in the ui
            output.close()
            raise NotImplementedError
        output.close()

    def get_images(self, dataset_id, image_id):
        url = self.url('/api/v1/ui/datasets/{}/images/{}/annotations/').format(dataset_id, image_id)
        content = self.get(url).json()
        image_url = self.url(content['image'])
        return self.get(image_url)   
    
    def search_images(self, class_name, annotation_task, num_data=None):
        task = annotation_task.value.replace(" ", "%20")
        url = self.url('/api/v1/ui/search/?classes={}&tasks={}').format(class_name, task)
        results = self.get(url).json()['results']
        return results
