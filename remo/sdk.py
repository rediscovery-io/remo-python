import csv
from operator import itemgetter
from typing import List, Callable, Union

from .domain import Image, Dataset, AnnotationSet, class_encodings, Annotation
from .api import API
from .browser import browse
from .endpoints import frontend
from .exporter import get_json_to_csv_exporter


class SDK:
    """
    Creates sdk object, and checks connection to server

    Args:
        server: server host name, e.g. ``http://localhost:8123/``
        email: user credentials
        password: user credentials
        browse: allows to choose between browser and electron viewer
    """

    def __init__(self, server: str, email: str, password: str, browse: Callable[[str], None] = browse):
        self.api = API(server, email, password)
        self.browse = browse

    def create_dataset(
        self,
        name: str,
        local_files: List[str] = None,
        paths_to_upload: List[str] = None,
        urls: List[str] = None,
        annotation_task: str = None,
        class_encoding=None,
    ) -> Dataset:
        """ 
        Creates a new dataset in Remo and optionally populate it with images and annotations.
        To be able add annotations, you need to provide annotation task.

        Args:
            name: name of the dataset.

            local_files: list of files or directories.
                These files will be linked.
                Folders will be recursively scanned for image files: ``jpg``, ``png``, ``tif``.

            paths_to_upload: list of files or directories.
                These files will be copied. Supported files: images, annotations and archives.

                - image files: ``jpg``, ``png``, ``tif``.
                - annotation files: ``json``, ``xml``, ``csv``.
                - archive files: ``zip``, ``tar``, ``gzip``.
                    Unpacked archive will be scanned for images, annotations and nested archives.

            urls: list of urls pointing to downloadable target, which can be image, annotation file or archive.

            annotation_task: specifies annotation task. See also: :class:`remo.task`.

            class_encoding: specifies how to convert class labels in annotation files to classes.
                See also: :class:`remo.class_encodings`.

        Returns:
            :class:`remo.Dataset`
        """

        json_data = self.api.create_dataset(name)
        ds = Dataset(self, id=json_data.get('id'), name=json_data.get('name'))
        ds.add_data(
            local_files, paths_to_upload, urls, annotation_task=annotation_task, class_encoding=class_encoding
        )
        ds.fetch()
        # TODO: there is a problem in fetching annotation sets
        return ds

    def add_data_to_dataset(
        self,
        dataset_id: int,
        local_files: List[str] = None,
        paths_to_upload: List[str] = None,
        urls: List[str] = None,
        annotation_task: str = None,
        folder_id: int = None,
        annotation_set_id: int = None,
        class_encoding=None,
    ) -> dict:
        """
        Adds images and/or annotations into existing dataset.
        To be able add annotations, you need to provide annotation task.

        Args:
            dataset_id: id of the desired dataset to extend

            local_files: list of files or directories.
                These files will be linked.
                Folders will be recursively scanned for image files: ``jpg``, ``png``, ``tif``.

            paths_to_upload: list of files or directories.
                These files will be copied. Supported files: images, annotations and archives.

                - image files: ``jpg``, ``png``, ``tif``.
                - annotation files: ``json``, ``xml``, ``csv``.
                - archive files: ``zip``, ``tar``, ``gzip``.
                    Unpacked archive will be scanned for images, annotations and nested archives.

            urls: list of urls pointing to downloadable target, which can be image, annotation file or archive.

            annotation_task: specifies annotation task. See also: :class:`remo.task`.

            folder_id: specifies target folder in the dataset.

            annotation_set_id: specifies target annotation set in the dataset.

            class_encoding: specifies how to convert class labels in annotation files to classes.
                See also: :class:`remo.class_encodings`.

        Returns:
            Dictionary with results for linking files, upload files and upload urls::

                {
                    'files_link_result': ...,
                    'files_upload_result': ...,
                    'urls_upload_result': ...
                }

        """
        result = {}
        kwargs = {
            'annotation_task': annotation_task,
            'folder_id': folder_id,
            'annotation_set_id': annotation_set_id,
        }

        if local_files:
            self._raise_value_error(local_files, 'local_files', list, 'list of paths')
            encoding = class_encodings.for_linking(class_encoding)
            result['files_link_result'] = self.api.upload_local_files(
                dataset_id, local_files, class_encoding=encoding, **kwargs
            )

        if paths_to_upload:
            self._raise_value_error(paths_to_upload, 'paths_to_upload', list, 'list of paths')
            encoding = class_encodings.for_upload(class_encoding)
            result['files_upload_result'] = self.api.bulk_upload_files(
                dataset_id, paths_to_upload, class_encoding=encoding, **kwargs
            )

        if urls:
            self._raise_value_error(urls, 'urls', list, 'list of URLs')
            encoding = class_encodings.for_linking(class_encoding)
            result['urls_upload_result'] = self.api.upload_urls(
                dataset_id, urls, class_encoding=encoding, **kwargs
            )

        return result

    @staticmethod
    def _raise_value_error(value, value_name, expected_type, expected_description):
        if not isinstance(value, expected_type):
            raise ValueError(
                'Parameter "{}" should be a {}, but instead is a {}.'.format(
                    value_name, expected_description, type(value)
                )
            )

    def list_datasets(self) -> List[Dataset]:
        """
        Lists the available datasets

        Returns:
            List[:class:`remo.Dataset`]
        """
        resp = self.api.list_datasets()
        return [
            Dataset(self, id=dataset['id'], name=dataset['name'], quantity=dataset['quantity'])
            for dataset in resp.get('results', [])
        ]

    def get_dataset(self, dataset_id: int) -> Dataset:
        """
        Retrieve dataset for giving dataset id.

        Args:
            dataset_id: dataset id

        Returns:
            :class:`remo.Dataset`
        """
        resp = self.api.get_dataset(dataset_id)
        dataset = Dataset(self, id=resp['id'], name=resp['name'], quantity=resp['quantity'])
        dataset._initialize_annotation_set()
        dataset._initialise_annotations()
        dataset._initialise_images()
        return dataset

    def list_annotation_sets(self, dataset_id: int) -> List[AnnotationSet]:
        """
        List annotation sets for giving dataset.

        Args:
            dataset_id: dataset id

        Returns:
            List[:class:`remo.AnnotationSet`]
        """

        result = self.api.list_annotation_sets(dataset_id)
        return [
            AnnotationSet(
                self,
                id=annotation_set['id'],
                name=annotation_set['name'],
                updated_at=annotation_set['updated_at'],
                task=annotation_set['task']['name'],
                dataset_id=dataset_id,
                top3_classes=annotation_set['statistics']['top3_classes'],
                total_images=annotation_set['statistics']['annotated_images_count'],
                total_classes=annotation_set['statistics']['total_classes'],
                total_annotation_objects=annotation_set['statistics']['total_annotation_objects'],
            )
            for annotation_set in result.get('results', [])
        ]

    def get_annotation_set(self, id: int) -> AnnotationSet:
        """
        Retrieves annotation set

        Args:
            id: annotation set id

        Returns:
             :class:`remo.AnnotationSet`
        """
        annotation_set = self.api.get_annotation_set(id)
        return AnnotationSet(
            self,
            id=annotation_set['id'],
            name=annotation_set['name'],
            updated_at=annotation_set['updated_at'],
            task=annotation_set['task']['name'],
            dataset_id=annotation_set['dataset']['id'],
            total_classes=len(annotation_set['classes']),
        )

    def export_annotations(
        self,
        annotation_set_id: int,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: str = 'true',
    ):
        """
        Exports annotations in given format

        Args:
            annotation_set_id: annotation set id
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            full_path: uses full image path (e.g. local path), can be one of ['true', 'false'], default='false'
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'

        Returns:
            annotation file content
        """
        return self.api.export_annotations(
            annotation_set_id,
            annotation_format=annotation_format,
            export_coordinates=export_coordinates,
            full_path=full_path,
        )

    def get_annotation_info(self, dataset_id: int, annotation_set_id: int, image_id: int) -> list:
        """
        Returns current annotations for the image

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id
            image_id: image id

        Returns:
            annotations info - list of annotation objects or classes
        """
        resp = self.api.get_annotation_info(dataset_id, annotation_set_id, image_id)
        return resp.get('annotation_info', [])

    def get_annotation(self, dataset_id: int, annotation_set_id: int, image_id: int) -> Annotation:
        """
        Returns annotation for giving image

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id
            image_id: image id

        Returns:
             :class:`remo.Annotation`
        """
        annotation_items = self.get_annotation_info(dataset_id, annotation_set_id, image_id)
        img = self.get_image_by_id(image_id)
        if not img:
            return None

        annotation = Annotation(img_filename=img.name)
        for item in annotation_items:
            if 'lower' in item:
                class_name = item.get('name')
                annotation.add_item(classes=[class_name])
            else:
                bbox = item.get('coordinates')
                bbox = [bbox[0]['x'], bbox[0]['y'], bbox[1]['x'], bbox[1]['y']]
                classes = [cls.get('name') for cls in item.get('classes', [])]
                annotation.add_item(classes=classes, bbox=bbox)
        return annotation

    def get_annotations(self, dataset_id: int, annotation_set_id: int) -> List[Annotation]:
        """
        Returns all annotations for giving annotation set

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id

        Returns:
             List[:class:`remo.Annotation`]
        """
        images = self.get_all_dataset_images(dataset_id)
        return [self.get_annotation(dataset_id, annotation_set_id, img.id) for img in images]

    def create_annotation_set(
        self, annotation_task: str, dataset_id: int, name: str, classes: List[str]
    ) -> AnnotationSet:
        """
        Creates a new annotation set

        Args:
            annotation_task: specified task for the annotation set. See also: :class:`remo.task`
            dataset_id: dataset id
            name: name of the annotation set
            classes: list of classes.

        Returns:
            :class:`remo.AnnotationSet`
        """
        annotation_set = self.api.create_annotation_set(annotation_task, dataset_id, name, classes)
        if 'error' in annotation_set:
            print('ERROR:', annotation_set['error'])
            return None

        return AnnotationSet(
            self,
            id=annotation_set['id'],
            name=annotation_set['name'],
            task=annotation_set['task'],
            dataset_id=annotation_set['dataset_id'],
            total_classes=len(annotation_set['classes']),
        )

    def add_annotation(self, annotation_set_id: int, image_id: int, annotation: Annotation):
        """
        Adds annotation to the giving image

        Args:
            annotation_set_id: annotation set id
            image_id: image id
            annotation: Annotation object
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        dataset_id = annotation_set.dataset_id

        annotation_info = self.get_annotation_info(dataset_id, annotation_set_id, image_id)
        object_id = len(annotation_info)

        objects = []
        classes = []

        for item in annotation.items:
            if item.bbox:
                objects.append(
                    {
                        "name": "OBJ " + str(object_id),
                        "coordinates": [
                            {"x": item.bbox.xmin, "y": item.bbox.ymin},
                            {"x": item.bbox.xmax, "y": item.bbox.ymax},
                        ],
                        "auto_created": False,
                        "position_number": object_id,
                        "classes": [
                            {"name": cls, "lower": cls.lower(), "questionable": False} for cls in item.classes
                        ],
                        "objectId": object_id,
                        "isHidden": False,
                    }
                )
                object_id += 1
            else:
                classes += [
                    {"name": cls, "lower": cls.lower(), "questionable": False} for cls in item.classes
                ]

        return self.api.add_annotation(
            dataset_id, annotation_set_id, image_id, annotation_info, classes=classes, objects=objects
        )

    def list_annotation_classes(self, annotation_set_id: int) -> List[str]:
        """
        List classes within the annotation set

        Args:
            annotation_set_id: annotation set id

        Returns:
            list of classes
        """
        json_data = self.api.list_annotation_classes(annotation_set_id)
        results = json_data.get('results', [])
        return list(map(itemgetter('class'), results))

    def export_annotation_to_csv(self, annotation_set_id: int, output_file: str, dataset: Dataset):
        """
        .. deprecated:: 0.0.13
            Use :func:`export_annotations` instead.

        Takes annotations and saves as a .csv file

        Args:
            annotation_set_id: annotation set id
            output_file: output .csv file path
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        exporter = get_json_to_csv_exporter(annotation_set.task)
        if not exporter:
            print(
                "ERROR: for giving annotation task '{}' export function not implemented".format(
                    annotation_set.task
                )
            )
            return

        annotation_results = dataset.annotations

        with open(output_file, 'w', newline='') as output:
            csv_writer = csv.writer(output)
            exporter(annotation_results, csv_writer)

    def list_dataset_images(self, dataset_id: int, folder_id: int = None, limit: int = None) -> list:
        """
        Given a dataset id returns list of the dataset images
        
        Args:
            dataset_id: dataset id
            folder_id: folder id
            limit: the number of images to be listed.

        Returns:
            list of images with their names and ids
        """

        if folder_id:
            result = self.api.list_dataset_contents_by_folder(dataset_id, folder_id, limit=limit)
        else:
            result = self.api.list_dataset_contents(dataset_id, limit=limit)

        images = [{'id': entry.get('id'), 'name': entry.get('name'),} for entry in result.get('results', [])]
        return images

    def get_all_dataset_images(self, dataset_id: int) -> List[Image]:
        """
        Returns all images for giving dataset.

        Args:
            dataset_id: dataset id

        Returns:
             List[:class:`remo.Image`]
        """
        json_data = self.api.get_all_dataset_images(dataset_id)
        if 'error' in json_data:
            print(
                'ERROR: failed to get all images for dataset id:{}, error: {}'.format(
                    dataset_id, json_data.get('error')
                )
            )
            return None

        return [Image(self, id=img.get('id'), name=img.get('name')) for img in json_data.get('results', [])]

    def get_images_by_id(self, dataset_id: int, image_id: int) -> bytes:
        """
        Get image file content by dataset_id and image_id

        Args:
            dataset_id: int
            image_id: int

        Returns:
            image binary data
        """
        return self.api.get_images_by_id(dataset_id, image_id)

    def get_image(self, url: str) -> bytes:
        """
        Get image file content by url

        Args:
            url: image url

        Returns:
            image binary data
        """
        return self.api.get_image(url)

    def get_image_by_id(self, image_id: int) -> Image:
        """
        Retrieves image by giving id.

        Args:
            image_id: image id

        Returns:
            :class:`remo.Image`
        """
        json_data = self.api.get_image_by_id(image_id)
        if 'error' in json_data:
            print('ERROR: failed to get image by id:{}, err: {}'.format(image_id, json_data.get('error')))
            return None

        return Image(self, id=json_data.get('id'), name=json_data.get('name'))

    def search_images(
        self,
        classes: Union[str, List[str]] = None,
        task: str = None,
        dataset_id: int = None,
        limit: int = None,
    ):
        """
        Search images by class and annotation task

        Args:
            classes: name of the classes to filter dataset.
            task: name of the annotation task to filter dataset
            dataset_id: narrows search result to giving dataset
            limit: limits number of search results

        Returns:
            image_id, dataset_id, name, annotations
        """
        return self.api.search_images(classes, task, dataset_id, limit)

    def view_search(self, cls=None, task=None):
        """
        Opens browser in search page
        """
        self._view(frontend.search)

    def view_image(self, image_id: int, dataset_id: int):
        """
        Opens browser on the image view for giving image

        Args:
            image_id: image id
            dataset_id: dataset id
        """
        # TODO: find easier way to check if image belongs to dataset
        img_list = self.list_dataset_images(dataset_id)
        contain = False

        for img_dict in img_list:
            if image_id == img_dict['id']:
                contain = True
                break

        if contain:
            self._view(frontend.image_view.format(image_id, dataset_id))
        else:
            print('Image ID: {} not in dataset {}'.format(image_id, dataset_id))

    def open_ui(self):
        """
        Opens the main page of Remo
        """
        self._view(frontend.datasets)

    def view_dataset(self, id: int):
        """
        Opens browser for the given dataset

        Args:
            id: dataset id
        """
        self._view(frontend.datasets, id)

    def view_annotation_set(self, id: int):
        """
        Opens browser in annotation view for the given annotation set

        Args:
            id: annotation set id
        """
        self._view(frontend.annotation, id)

    def view_annotation_stats(self, annotation_set_id: int):
        """
        Opens browser in annotation statistics view for the given annotation set

        Args:
            annotation_set_id: annotation set id
        """
        self._view(frontend.annotation_detail.format(annotation_set_id))

    def _view(self, url, *args, **kwargs):
        self.browse(self.api.url(url, *args, **kwargs))
