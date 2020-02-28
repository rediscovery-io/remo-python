from io import BytesIO
from copy import deepcopy
from typing import List, TypeVar, Callable

from .annotation import Annotation
from .image import Image

AnnotationSet = TypeVar('AnnotationSet')


class Dataset:
    """
    Remo dataset

    Args:
        id: dataset id
        name: dataset name
        quantity: number of images
    """

    def __init__(self, sdk, id: int = None, name: str = None, quantity: int = 0):
        self.sdk = sdk
        self.id = id
        self.name = name
        self.images = []
        self.annotation_sets = []
        self.default_annotation_set = None
        self.annotations = []
        self.images_dict = {}
        self.images_by_id = {}
        try:
            self.quantity = int(quantity)
        except (ValueError, TypeError):
            self.quantity = 0
        # TODO: find images quick by ids and by name

    def __str__(self):
        return "Dataset {id} - '{name}'".format(id=self.id, name=self.name)

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        # return len(self.images)
        return len(self.annotations)

    def __getitem__(self, sliced):
        # TODO: add exception for the original dataset specific methods.

        self._initialise_annotations()
        new_self = deepcopy(self)
        new_self.images = self.images[sliced]
        if not isinstance(new_self.images, list):
            new_self.images = [new_self.images]

        new_img_name_list = [img.name for img in new_self.images]
        new_self.annotations = list(
            filter(lambda annotation: annotation.get('file_name') in new_img_name_list, self.annotations)
        )

        return new_self

    def add_data(
        self,
        local_files: List[str] = None,
        paths_to_upload: List[str] = None,
        urls: List[str] = None,
        annotation_task: str = None,
        folder_id: int = None,
        annotation_set_id: int = None,
        class_encoding=None,
    ) -> dict:
        """
        Adds images and/or annotations into dataset.
        To add annotations you need to specify an annotation task.

        Args:
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

        return self.sdk.add_data_to_dataset(
            self.id,
            local_files=local_files,
            paths_to_upload=paths_to_upload,
            urls=urls,
            annotation_task=annotation_task,
            folder_id=folder_id,
            annotation_set_id=annotation_set_id,
            class_encoding=class_encoding,
        )

    def fetch(self):
        """
        Updates dataset information from server
        """
        dataset = self.sdk.get_dataset(self.id)
        self.__dict__.update(dataset.__dict__)

    def list_annotation_sets(self) -> List[AnnotationSet]:
        """
        Lists the annotation sets within the dataset

        Returns:
            List[:class:`remo.AnnotationSet`]
        """
        return self.sdk.list_annotation_sets(self.id)

    def export_annotations(
        self,
        annotation_set_id: int = None,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: str = 'true',
    ):
        """
        Export annotations

        Args:
            annotation_set_id: annotation set id, by default will be used default_annotation_set
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            full_path: uses full image path (e.g. local path), can be one of ['true', 'false'], default='false'

        Returns:
            annotation file content
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.export_annotations(
                annotation_format=annotation_format,
                export_coordinates=export_coordinates,
                full_path=full_path,
            )

        print('ERROR: annotation set not defined')

    def get_annotation(self, dataset_id: int, annotation_set_id: int, image_id: int) -> Annotation:
        """
        Retrieves annotation for a given image

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id
            image_id: image id

        Returns:
            :class:`remo.Annotation`
        """
        items = self.sdk.get_annotation_info(dataset_id, annotation_set_id, image_id)
        image_name = self.images_by_id.get(image_id)
        if not image_name:
            print('ERROR: Image with id - {}, was not found'.format(image_id))
            return None

        annotation = Annotation(img_filename=image_name)
        for item in items:
            if 'lower' in item:
                class_name = item.get('name')
                annotation.add_item(classes=[class_name])
            else:
                bbox = item.get('coordinates')
                bbox = [bbox[0]['x'], bbox[0]['y'], bbox[1]['x'], bbox[1]['y']]
                classes = [cls.get('name') for cls in item.get('classes', [])]
                annotation.add_item(classes=classes, bbox=bbox)
        return annotation

    def create_annotation_set(
        self, annotation_task: str, name: str, classes: List[str], path_to_annotation_file: str = None
    ) -> AnnotationSet:
        """
        Creates a new annotation set.
        If path_to_annotation_file is provided, it populates it with the given annotations.

        Args:
            annotation_task: annotation task. See also: :class:`remo.task`
            name: annotation set name
            classes: list of classes. Example: ['Cat', 'Dog']
            path_to_annotation_file: path to .csv annotation file

        Returns:
            :class:`remo.AnnotationSet`
        """
        annotation_set = self.sdk.create_annotation_set(annotation_task, self.id, name, classes)

        if annotation_set and path_to_annotation_file:
            self.add_data(
                paths_to_upload=[path_to_annotation_file],
                annotation_task=annotation_task,
                annotation_set_id=annotation_set.id,
            )

            annotation_set = self.sdk.get_annotation_set(annotation_set.id)

        return annotation_set

    def add_annotations_from_file(
        self,
        file_path: str,
        parser_function: Callable[[str], List[Annotation]],
        annotation_set_id: int = None,
    ):
        """
        Uploads annotations from a custom annotation file to an annotation set.
        If using a supported annotation format, you can directly use :func:`add_data` function

        Args:
            file_path: path to annotation file to upload
            parser_function: function which receives file_path and returns a List[:class:`remo.Annotation`]
            annotation_set_id: id of the annotation set to use

        Example::

            import csv
            from remo import Annotation

            def parser_function(file_path):
            '''
            File example:
            file_name,class_name
            000012dasd21e.jpg,Dog
            000012dasd221.jpg,Cat
            '''
                annotations = []
                with open(file_path, 'r') as f:
                    csv_file = csv.reader(f, delimiter=',')
                    for row in csv_file:
                        file_name, class_name = row
                        annotation = Annotation(img_filename=file_name)
                        annotation.add_item(classes=[class_name])
                        annotations.append(annotation)
                return annotations

        """

        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if not annotation_set:
            print('ERROR: Annotation set was not found')
            return

        annotations = parser_function(file_path)

        for annotation in annotations:
            image_id = self.images_dict.get(annotation.img_filename)
            if not image_id:
                print('WARNING: Image {} was not found in {}'.format(annotation.img_filename, self))

            self.sdk.add_annotation(annotation_set_id, image_id, annotation)

    def get_annotation_set(self, id: int) -> AnnotationSet:
        """
        Retrieves annotation set with given id

        Args:
            id: annotation set id

        Returns:
             :class:`remo.AnnotationSet`
        """

        for annotation_set in self.annotation_sets:
            if annotation_set.id == id:
                return annotation_set

        annotation_set = self.sdk.get_annotation_set(id)
        if annotation_set.dataset_id == self.id:
            self.annotation_sets.append(annotation_set)
            return annotation_set

        print('ERROR: annotation set with id={} was not found'.format(id))

    def _get_annotation_set_or_default(self, annotation_set_id: int = None) -> AnnotationSet:
        """
        Retrieves default annotation set, or the annotation set with the given id

        Args:
            annotation_set_id: annotation set id

        Returns:
             :class:`remo.AnnotationSet`
        """
        if not annotation_set_id:
            return self.default_annotation_set

        return self.get_annotation_set(annotation_set_id)

    def get_annotation_statistics(self, annotation_set_id: int = None):
        """
        Prints annotation statistics of all the available annotation sets within the dataset

        Returns:
            list of dictionaries with fields annotation set id, name, num of images, num of classes, num of objects, top3 classes, release and update dates
        """

        # TODO: ALR - Improve output formatting
        # TODO: ALR - Optional annotation set id as input
        statistics = []
        for ann_set in self.annotation_sets:

            if (annotation_set_id is None) or (annotation_set_id == ann_set.id):
                stat = {
                    'AnnotationSet ID': ann_set.id,
                    'AnnotationSet name': ann_set.name,
                    'n_images': ann_set.total_images,
                    'n_classes': ann_set.total_classes,
                    'n_objects': ann_set.total_annotation_objects,
                    'top_3_classes': ann_set.top3_classes,
                    'creation_date': ann_set.released_at,
                    'last_modified_date': ann_set.updated_at,
                }

                statistics.append(stat)
        return statistics

    def list_classes(self, annotation_set_id: int = None) -> List[str]:
        """
        Lists all the classes within the dataset

        Args:
             annotation_set_id: annotation set id. If not specified the default annotation set is considered.

        Returns:
            List of classes
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.get_classes()

        print('ERROR: annotation set not defined')

    def export_annotation_to_csv(self, output_file: str, annotation_set_id: int = None):
        """
        .. deprecated:: 0.0.13
            Use :func:`export_annotations` instead.

        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.export_annotation_to_csv(output_file, self)

        print('ERROR: annotation set not defined')

    def set_default_annotations(self, annotation_set_id: int):
        """
        Sets default annotation set
        """
        self.default_annotation_set = self.get_annotation_set(annotation_set_id)

    def _initialise_images(self):
        self.images = self.list_images()

        for item in self.images:
            self.images_dict[item.name] = item.id
            self.images_by_id[item.id] = item.name

    def _initialize_annotation_set(self):
        """
        Initializes the default annotation set for the dataset to the first-created annotation set
        """
        self.annotation_sets = self.sdk.list_annotation_sets(self.id)
        if self.annotation_sets:
            self.default_annotation_set = self.annotation_sets[0]

    def _initialise_annotations(self, annotation_set_id: int = None):
        """
        Initializes annotations of the dataset. If a annotation set id is not specified, it assigns annotations to the default annotation set.

        Args:
            annotation_set_id: annotation set id
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            self.annotations = self.export_annotations(annotation_set.id)

    def get_annotations(self, annotation_set_id: int = None) -> List[Annotation]:
        """
        Returns all annotations for the default or given annotation set.
        If no annotation set is specified, the default annotation set will be used

        Args:
            annotation_set_id: annotation set id

        Returns:
             List[:class:`remo.Annotation`]
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return self.sdk.get_annotations(self.id, annotation_set.id)
        print('ERROR: annotation set was not defined.')

    def list_images(self, limit: int = None, offset: int = None) -> List[Image]:
        """
        Given a dataset id returns list of the dataset images

        Args:
            limit: the number of images to be listed
            offset: specifies offset

        Returns:
            List[:class:`remo.Image`]
        """
        return self.sdk.list_dataset_images(self.id, limit=limit, offset=offset)

    def get_images_by_id(self, image_id: int) -> bytes:
        """
        Retrieves content for a given image

        Args:
            image_id: image id

        Returns:
            image content
        """
        # TODO: turn into an image object
        r = self.sdk.get_images_by_id(self.id, image_id)
        return BytesIO(r.content)

    def get_images_by_search(self, class_list: List[str], task: str):
        #  TODO: doesn't work
        """
        Given a list of classes and annotation task, it returns a list of all the images with mathcing annotations

        Args:
            class_list: list of classes
            task: annotation task. See also: :class:`remo.task`

        Returns:
            list of dictionaries containing classes, task and image content
        """
        # TODO: add tags
        # TODO: turn into an image object
        result = self.search(class_list, task)
        img_list = []
        for i in range(len(result)):
            content = self.sdk.get_image_content(result.images[i]['preview'])
            img_list.append({'classes': result.annotations[i]['classes'], 'task': task, 'img': content})
        return img_list

    def search(self, class_list: List[str], task: str):
        """
        Given a list of classes and annotation task, it returns a list of all the images with mathcing annotations
        
        Args:
            class_list: list of classes with the same images
            task: annotation task. See also: :class:`remo.task`

        Returns:
            subset of the dataset
        """
        # TODO: add exception for the original dataset specific methods.
        result = self.sdk.search_images(class_list, task, self.id)
        filtered_dataset = deepcopy(self)

        new_img_name_list = [im.get('name') for im in result]
        filtered_dataset.images = list(filter(lambda im: im.name in new_img_name_list, self.images))
        filtered_dataset.annotations = list(
            filter(lambda annotation: annotation.get('file_name') in new_img_name_list, self.annotations)
        )

        return filtered_dataset

    def view(self):
        """
        Opens browser on dataset page
        """
        self.sdk.view_dataset(self.id)

    def view_annotate(self, annotation_set_id: int = None):
        """
        Opens browser on the annotation tool for the given annotation set

        Args:
              annotation_set_id: annotation set id. If not specified, default one be used.
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            annotation_set.view()

    def view_annotation_statistics(self, annotation_set_id: int = None):
        """
        Opens browser on annotation set statistics page

        Args:
            annotation_set_id: annotation set id. If not specified, default one be used.
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            annotation_set.view_stats()

    def view_image(self, image_id: int):
        """
        Opens browser on image view page for the given image

        Args:
            image_id: image id
        """
        self.sdk.view_image(image_id, self.id)
