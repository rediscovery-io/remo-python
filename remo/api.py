import http
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import filetype
import requests
import urllib.parse

from .domain import task
from .endpoints import backend
from .utils import FileResolver


class UploadStatus:

    def __init__(self, total_count):
        self.total_count = total_count
        self.current_count = 0
        self.start = datetime.now()
        self.reported_progress = 0

    def update(self, count):
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


class BaseAPI:
    def __init__(self, server, email, password):
        self.server = server
        self.token = None
        self._login(email, password)

    def _login(self, email, password):
        try:
            resp = requests.post(self.url(backend.login),
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
            raise Exception('Not authenticated')
        return {'Authorization': 'Token {}'.format(self.token)}

    def url(self, endpoint, *args, **kwargs):
        return self._build_url(self.server, endpoint, *args, **kwargs)

    def post(self, *args, **kwargs):
        return requests.post(*args, headers=self._auth_header(), **kwargs)

    def get(self, *args, **kwargs):
        return requests.get(*args, headers=self._auth_header(), **kwargs)

    @staticmethod
    def _build_url(*args, **kwargs):
        """
        Builds full url from inputs.
        Additional param `tail_slash` specifies tailed slash

        :param args: typically server and endpoint
        :param kwargs: additional query parameters
        :return: full url
        """
        args = list(filter(lambda arg: arg is not None, args))
        tail_slash = kwargs.pop('tail_slash', (str(args[-1])[-1] == '/'))
        url = '/'.join(map(lambda x: str(x).strip('/'), args))

        params = []
        for key, val in kwargs.items():
            if val:
                params.append('{}={}'.format(key, val))

        if len(params):
            joined_params = "&".join(params)
            separator = '&' if '?' in url else '/?'
            url = "{}{}{}".format(url, separator, urllib.parse.quote(joined_params))
        elif '?' not in url and tail_slash:
            url += '/'

        return url


class API(BaseAPI):

    def create_dataset(self, name):
        return self.post(self.url(backend.dataset), json={"name": name}).json()

    def upload_file(self, dataset_id, path, annotation_task=None, folder_id=None):
        name = os.path.basename(path)
        files = {'files': (name, open(path, 'rb'), filetype.guess_mime(path))}
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task

        url = self.url(backend.dataset_upload.format(dataset_id), folder_id=folder_id)
        return self.post(url, files=files, data=data).json()

    # TODO: fix progress to include both local files and uploads
    def upload_files(self, dataset_id, files_to_upload=[], annotation_task=None, folder_id=None, status=None):
        files = [('files', (os.path.basename(path), open(path, 'rb'), filetype.guess_mime(path))) for path in
                 files_to_upload]
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task

        url = self.url(backend.dataset_upload.format(dataset_id), folder_id=folder_id)

        r = self.post(url, files=files, data=data)

        if r.status_code != http.HTTPStatus.OK:
            print('Possible Error - Response:', r.text, 'files:', files_to_upload)

        status.update(len(files))
        status.progress()
        return r.json()

    # TODO: fix progress to include both local files and uploads
    def bulk_upload_files(self, dataset_id, files_to_upload, annotation_task=None, folder_id=None):

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

    def split_files_by_size(self, files):
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
            payload['annotation_task'] = annotation_task
        if folder_id:
            payload['folder_id'] = folder_id

        url = self.url(backend.dataset_upload.format(dataset_id))
        return self.post(url, json=payload).json()

    def upload_urls(self, dataset_id, urls, annotation_task=None, folder_id=None):
        payload = {"urls": urls}
        if annotation_task:
            payload['annotation_task'] = annotation_task
        if folder_id:
            payload['folder_id'] = folder_id

        url = self.url(backend.dataset_upload.format(dataset_id))
        return self.post(url, json=payload).json()

    def list_datasets(self):
        url = self.url(backend.v1_datasets)
        return self.get(url).json()

    def list_dataset_contents(self, dataset_id, **kwargs):
        url = self.url(backend.v1_dataset_images.format(dataset_id), **kwargs)
        return self.get(url).json()

    def list_dataset_contents_by_folder(self, dataset_id, folder_id, **kwargs):
        url = self.url(backend.dataset_folder_content.format(dataset_id, folder_id), **kwargs)
        return self.get(url).json()

    def get_dataset(self, id):
        url = self.url(backend.dataset,id)
        return self.get(url).json()

    def list_annotation_sets(self, dataset_id):
        url = self.url(backend.v1_dataset_annotation_sets.format(dataset_id))
        return self.get(url).json()

    def get_annotations(self, annotation_set_id, annotation_format='json'):
        """
        Args:
            annotation_format: can be one of ['json', 'coco'], default='json'
        Returns: annotations
        """
        url = self.url(backend.v1_export_annotations.format(annotation_set_id, annotation_format))
        return self.get(url).json()

    # TODO: seems like this func should go to sdk
    def export_annotation_to_csv(self, annotation_set_id, output_file, annotation_task):
        annotation = self.get_annotations(annotation_set_id, annotation_format='json')
        output = open(output_file, 'w', newline='')
        f = csv.writer(output)
        if annotation_task == task.object_detection:
            header = ['file_name', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
            f.writerow(header)
            for item in annotation:
                annotations = item['annotations']
                for annotation in annotations:
                    classes = annotation['classes']
                    for cls in classes:
                        f.writerow([item['file_name'], cls] + list(annotation['bbox'].values()))
        elif annotation_task == task.instance_segmentation:
            header = ['file_name', 'class', 'coordinates']
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
        url = self.url(backend.v1_dataset_image_annotations.format(dataset_id, image_id))
        content = self.get(url).json()
        image_url = self.url(content['image'])
        return self.get(image_url)

    def search_images(self, class_name, annotation_task, num_data=None):
        # TODO: check if this needed
        # task = annotation_task.replace(" ", "%20")
        url = self.url(backend.v1_search, classes=class_name, tasks=task)
        results = self.get(url).json()['results']
        return results
