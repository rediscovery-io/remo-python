import http
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import filetype
import requests
from urllib.parse import quote

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
            if type(val) is str:
                if ',' in val:
                    values = val.split(',')
                    values = ','.join(map(quote, values))
                    params.append('{}={}'.format(key, values))
                else:
                    params.append('{}={}'.format(key, quote(val)))
            elif type(val) is list:
                values = ','.join(map(lambda v: quote(str(v)), val))
                params.append('{}={}'.format(key, values))
            elif val:
                params.append('{}={}'.format(key, val))

        if len(params):
            joined_params = "&".join(params)
            separator = '&' if '?' in url else '/?'
            url = "{}{}{}".format(url, separator, joined_params)
        elif '?' not in url and tail_slash:
            url += '/'

        return url


class API(BaseAPI):

    def create_dataset(self, name):
        return self.post(self.url(backend.dataset), json={"name": name}).json()

    def create_annotation_set(self, annotation_task, dataset_id, name, classes=[]):
        """
        Creates a new empty annotation set
        Args:
            - annotation_task: str.
                name of the annotation task
            - dataset_id: int.
                the id of the dataset to create new annotation set
            - name: str.
                Name of the annotation set to create.
            - classes: list of str.
                list of classes.
                Example: ['Cat', 'Dog']
        """

        payload = {
            "annotation_task": annotation_task,
            "classes": classes,
            "dataset_id": dataset_id,
            "name": name
        }

        return self.post(self.url(backend.v1_create_annotation_set), json=payload).json()

    def add_annotation(self, dataset_id, annotation_set_id, image_id, cls, coordinates=None, object_id=None):
        # WARNING: this function replaces existing annotations
        # TODO: get dataset_id from annotation_set_id
        """
        Adds annotations to the specified annotation set
        Args:
           
            - image_id: int.
            - annotation_set_id: int.
            - cls: str. 
                class of the detected object
            - coordinates: list.
                list of dictionaries containing annotation coordinates.
            - object_id: int. Default None.
                id of the object in the given image. If not feed any value considered as Image classification task. 
        """
        url = self.url(backend.add_annotation).format(dataset_id, annotation_set_id, image_id)

        if object_id:
            # It's object detection
            payload = {"objects": [{"name": "OBJ " + str(object_id),
                                    "coordinates": [{"x": float(coordinates[0]), "y": float(coordinates[1])},
                                                    {"x": float(coordinates[2]), "y": float(coordinates[3])}],
                                    "auto_created": False,
                                    "position_number": object_id,
                                    "classes": [{"name": cls, "lower": cls.lower(), "questionable": False}],
                                    "objectId": object_id,
                                    "isHidden": False}]}
        else:
            # It's classification 
            payload = {"classes": [{"name": cls, "lower": cls.lower(), "questionable": False}]}

        return self.post(url, json=payload).json()

    def upload_file(self, dataset_id, path, annotation_task=None, folder_id=None):
        name = os.path.basename(path)
        files = {'files': (name, open(path, 'rb'), filetype.guess_mime(path))}
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task

        url = self.url(backend.dataset_upload.format(dataset_id), folder_id=folder_id)
        return self.post(url, files=files, data=data).json()

    # TODO: fix progress to include both local files and uploads
    def upload_files(self, dataset_id, files_to_upload=[], annotation_task=None, folder_id=None, status=None,
                     annotation_set_id=None, class_encoding=None):
        files = [('files', (os.path.basename(path), open(path, 'rb'), filetype.guess_mime(path))) for path in
                 files_to_upload]
        data = {}
        if annotation_task:
            data['annotation_task'] = annotation_task

        if isinstance(class_encoding, dict):
            for key, val in class_encoding.items():
                data['class_encoding_{}'.format(key)] = val

        url = self.url(backend.dataset_upload.format(dataset_id), folder_id=folder_id,
                       annotation_set_id=annotation_set_id)
        r = self.post(url, files=files, data=data)

        if r.status_code != http.HTTPStatus.OK:
            print('Possible Error - Response:', r.text, 'files:', files_to_upload)

        status.update(len(files))
        status.progress()
        return r.json()

    # TODO: fix progress to include both local files and uploads
    def bulk_upload_files(self, dataset_id, files_to_upload, annotation_task=None, folder_id=None,
                          annotation_set_id=None, class_encoding=None):

        # files to upload
        files = FileResolver(files_to_upload, annotation_task is not None).resolve()
        groups = self.split_files_by_size(files)
        status = UploadStatus(len(files))
        with ThreadPoolExecutor(1) as ex:
            res = ex.map(
                lambda bulk: self.upload_files(dataset_id, bulk, annotation_task, folder_id, status, annotation_set_id,
                                               class_encoding),
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

    def upload_local_files(self, dataset_id, local_files, annotation_task=None, folder_id=None, annotation_set_id=None,
                           class_encoding=None):
        payload = {"local_files": local_files}
        if annotation_task:
            payload['annotation_task'] = annotation_task
        if folder_id:
            payload['folder_id'] = folder_id
        if isinstance(class_encoding, dict):
            payload['class_encoding'] = class_encoding

        url = self.url(backend.dataset_upload.format(dataset_id), annotation_set_id=annotation_set_id)
        return self.post(url, json=payload).json()

    def upload_urls(self, dataset_id, urls, annotation_task=None, folder_id=None, annotation_set_id=None,
                    class_encoding=None):
        payload = {"urls": urls}
        if annotation_task:
            payload['annotation_task'] = annotation_task
        if folder_id:
            payload['folder_id'] = folder_id
        if isinstance(class_encoding, dict):
            payload['class_encoding'] = class_encoding

        url = self.url(backend.dataset_upload.format(dataset_id), annotation_set_id=annotation_set_id)
        return self.post(url, json=payload).json()

    def list_datasets(self):
        url = self.url(backend.v1_datasets)
        return self.get(url).json()

    def list_dataset_contents(self, dataset_id, **kwargs):
        # TODO: need to filter with annotation_set_id
        # TODO: remove kwargs, replace with limit url = self.url(backend.v1_dataset_images.format(dataset_id), limit=limit)
        url = self.url(backend.v1_dataset_images.format(dataset_id), **kwargs)
        return self.get(url).json()

    def list_dataset_contents_by_folder(self, dataset_id, folder_id, **kwargs):
        url = self.url(backend.dataset_folder_content.format(dataset_id, folder_id), **kwargs)
        return self.get(url).json()

    def get_dataset(self, id):
        url = self.url(backend.dataset, id, tail_slash=True)
        r = self.get(url)
        return r.json()

    def list_annotation_sets(self, dataset_id):
        url = self.url(backend.v1_dataset_annotation_sets.format(dataset_id))
        return self.get(url).json()

    def get_annotation_set(self, id):
        url = self.url(backend.v1_annotation_set.format(id))
        return self.get(url).json()

    def get_annotations(self, annotation_set_id, annotation_format='json'):
        """
        Args:
            annotation_format: can be one of ['json', 'coco'], default='json'
        Returns: annotations
        """
        url = self.url(backend.v1_export_annotations.format(annotation_set_id, annotation_format))
        return self.get(url).json()

    def list_annotation_classes(self, annotation_set_id=None):
        """
        Args:
            annotation_set_id: int. 
        Returns: list of classes
        """
        url = self.url(backend.v1_annotation_classes.format(annotation_set_id))
        return self.get(url).json()

    def get_images_by_id(self, dataset_id, image_id):
        url = self.url(backend.v1_dataset_image_annotations.format(dataset_id, image_id))
        content = self.get(url).json()
        image_url = self.url(content['image'])
        return self.get(image_url)

    def get_image(self, url):
        return self.get(self.url(url))

    def search_images(self, classes=None, task=None, dataset_id=None, limit=None):
        """
        Search images given a list of classes and tasks
        Args:
            classes: string or list of strings - search for images which matches to all giving classes
            task: string - annotation task
            dataset_id: int - performs search in giving dataset otherwise in all datasets
            limit: int - limits search result
        Returns: dictionary of image_id, dataset_id, name, preview, annotations, classes, dimensions
        """
        # TODO: adding task names on return
        params = {}
        if task:
            params['tasks'] = task
        if classes:
            params['classes'] = classes
        if dataset_id:
            params['dataset_id'] = dataset_id
        if limit:
            params['limit'] = limit

        url = self.url(backend.v1_search, **params)
        return self.get(url).json()['results']
