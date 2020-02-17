from io import BytesIO

from . import Annotation
from .image import Image
from copy import deepcopy


class Dataset:
    def __init__(self, sdk, id=None, name=None, quantity=None):
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
        except ValueError:
            self.quantity = 0
        # TODO: find images quick by ids and by name

    def __str__(self):
        return "Dataset {id} - '{name}'".format(id=self.id, name=self.name)

    def __len__(self):
        # return len(self.images)
        return len(self.annotations)

    def __getitem__(self, sliced):
        # TODO: add exception for the original dataset specific methods.
        self._initialise_annotations()
        new_self = deepcopy(self)
        new_self.images = self.images[sliced]

        new_img_name_list = [im.name for im in new_self.images]
        new_self.annotations = list(
            filter(lambda annotation: annotation.get('file_name') in new_img_name_list, self.annotations))

        return new_self

    def __repr__(self):
        return self.__str__()

    def add_data(self, local_files=[], paths_to_upload=[], urls=[], annotation_task=None, folder_id=None,
                 annotation_set_id=None, class_encoding=None):
        """
            
        Adds data to the dataset
        
        Args:
            - local_files: list of files or directories. Function will scan for .png, .jpeg, .tiff and .jpg in the folders and sub-folders.
            - paths_to_upload: list of files or directories. These files will be uploaded to the local disk.

               files supported: image files, annotation files and archive files.

               Annotation files: json, xml, csv. If annotation file is provided, you need to provide annotation task.

               Archive files: zip, tar, gzip. These files are unzipped, and then we scan for images, annotations and other archives. Support for nested archive files, image and annotation files in the same format supported elsewhere

            - urls: list of urls pointing to downloadable target, which should be an archive file. The function will download the target of the URL - then we scan for archive files, unpack them and proceed as per Archive file section.

            - annotation_task:
               object_detection = 'Object detection'. Supports Coco, Open Images, Pascal
               instance_segmentation = 'Instance segmentation'. Supports Coco
               image_classification = 'Image classification'. ImageNet
            - folder_id: if there is a folder in the target remo id, and you want to add images to a specific folder, you can specify it here.
        """

        return self.sdk.add_data_to_dataset(dataset_id=self.id,
                                            local_files=local_files,
                                            paths_to_upload=paths_to_upload,
                                            urls=urls,
                                            annotation_task=annotation_task,
                                            folder_id=folder_id,
                                            annotation_set_id=annotation_set_id,
                                            class_encoding=class_encoding)

    def fetch(self):
        dataset = self.sdk.get_dataset(self.id)
        self.__dict__.update(dataset.__dict__)

    def list_annotation_sets(self):
        """
        Lists of the annotation sets within the dataset
        Returns: list of annotations containing annotation set id-name, annotation task and num classes
        """
        return self.sdk.list_annotation_sets(self.id)

    def export_annotations(self, annotation_set_id=None, annotation_format='json', export_coordinates='pixel',
                           full_path='true'):
        """
        Export annotations
        
        Args:
            - annotation_set_id: int default: default_annotation_set
            - annotation_format: string. can be one of ['json', 'coco', 'csv'], default='json'
            - full_path: uses full image path (e.g. local path), can be one of ['true', 'false'], default='false'
            - export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'

        Returns: file_name, height, width, tags, task, annotations with classes and coordinates
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.export_annotations(annotation_format=annotation_format,
                                                     export_coordinates=export_coordinates, full_path=full_path)

        print('ERROR: annotation set not defined')

    def get_annotation(self, dataset_id, annotation_set_id, image_id) -> Annotation:
        """
        Returns annotation for giving image
        Args:
            dataset_id: dataset
            annotation_set_id:
            image_id:
        :return: Annotation
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

    def create_annotation_set(self, annotation_task, name, classes, path_to_annotation_file=None):
        """
        Creates a new empty annotation set and pushes the annotations if path_to_annotation_file is provided.
        Args:
            - annotation_task: str.
                annotation task chosen from ['Image classification', 'Object detection', 'Instance segmentation'] 
            - name: str.
                Name of the annotation set to create.
            - classes: list.
                example: ['Cat', 'Dog']
            - path_to_annotation_file: str.
                path to .csv file of the annotations
        """
        annotation_set = self.sdk.create_annotation_set(annotation_task, self.id, name, classes)
        if annotation_set is not None and path_to_annotation_file is not None:
            self.add_data(paths_to_upload=[path_to_annotation_file], annotation_task=annotation_task,
                          annotation_set_id=annotation_set.id)
            annotation_set = self.sdk.get_annotation_set(annotation_set.id)
        return annotation_set

    def add_annotations_from_file(self, file_path, parser_function, annotation_set_id=None):
        """
        Uploads annotations from a custom annotation file to an annotation set.
        For supported annotation files format it's easier to use `add_data` function
        
        Args:
            - file_path: path to annotation file to upload
            - parser_function: function which receives file_path and returns a list of remo.domain.Annotation objects
            - annotation_set_id: id of the annotation set to use

            Example:
                import csv
                from remo.domain import Annotation

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

    def get_annotation_set(self, id):
        for annotation_set in self.annotation_sets:
            if annotation_set.id == id:
                return annotation_set

        annotation_set = self.sdk.get_annotation_set(id)
        if annotation_set.dataset_id == self.id:
            self.annotation_sets.append(annotation_set)
            return annotation_set

        print('ERROR: annotation set with id={} was not found'.format(id))

    def _get_annotation_set_or_default(self, annotation_set_id=None):
        if not annotation_set_id:
            return self.default_annotation_set

        return self.get_annotation_set(annotation_set_id)

    def get_annotation_statistics(self, annotation_set_id=None):
        """
        #TODO ALR - Improve output formatting
        #TODO ALR - Optional annotation set id as input
        
        Prints annotation statistics of all the avaiable annotation sets of the dataset
        Returns: annotation set id, name, num of images, num of classes, num of objects, top3 classes, release and update dates
        """
        statistics = []
        for ann_set in self.annotation_sets:

            if (annotation_set_id is None) or (annotation_set_id == ann_set.id):
                stat = {}
                stat['AnnotationSet ID'] = ann_set.id
                stat['AnnotationSet name'] = ann_set.name
                stat['n_images'] = ann_set.total_images
                stat['n_classes'] = ann_set.total_classes
                stat['n_objects'] = ann_set.total_annotation_objects
                stat['top_3_classes'] = ann_set.top3_classes
                stat['creation_date'] = ann_set.released_at
                stat['last_modified_date'] = ann_set.updated_at

                statistics.append(stat)
        return statistics

    def list_classes(self, annotation_set_id=None):
        """
        Lists information of the classes within the dataset
        Args:
             - annotation_set_id: int. Default value:  None
                 id of annotation set for which to list the classes. If not specified the default annotation set is considered.
        Returns: List of dictionaries containing class name, total annotation object and total images
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.get_classes()

        print('ERROR: annotation set not defined')

    def export_annotation_to_csv(self, output_file, annotation_set_id=None):
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.export_annotation_to_csv(output_file, self)

        print('ERROR: annotation set not defined')

    def set_default_annotations(self, annotation_set_id):
        self.default_annotation_set = self.get_annotation_set(annotation_set_id)

    def _initialise_images(self):
        self.images = self.list_images()

        for item in self.images:
            self.images_dict[item.name] = item.id
            self.images_by_id[item.id] = item.name

    def _initialize_annotation_set(self):
        """
        Initializes the default annotation set to the first annotation set of the dataset.
        """
        self.annotation_sets = self.sdk.list_annotation_sets(self.id)
        if self.annotation_sets:
            self.default_annotation_set = self.annotation_sets[0]

    def _initialise_annotations(self, annotation_set_id=None):
        """
        Initializes annotations of the dataset. If annotation set is not specified, assigns annotations of the default annotation set.
        Args:
            - annotation_set_id: int.
                the id of the annotation set to query
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            self.annotations = self.export_annotations(annotation_set.id)

    def list_images(self, folder_id=None, limit=None):
        """
        Given a dataset id returns list of the dataset images
        Args:
            - dataset_id: int.
                the id of the dataset to query
            - folder_id: int.
                the id of the folder to query
            - limit: int.
                the number of images to be listed.
        Returns: list of images with their names and ids
        """
        if not limit:
            limit = self.quantity

        images = self.sdk.list_dataset_images(self.id, folder_id, limit=limit)

        # TODO: check the issue with Image.path
        return [
            Image(id=img.get('id'), path=img, dataset=self.name, name=img.get('name'))
            for img in images
        ]

    def get_images_by_id(self, image_id):
        """
        Given an image id returns the image content
        Args:
            - image_id: int
        Returns: image content
        """
        # TODO: turn into an image object
        r = self.sdk.get_images_by_id(self.id, image_id)
        return BytesIO(r.content)

    def get_images_by_search(self, class_list, task):
        """
        Given a class list and task returns image list 
        Args:
            - class_list: list of strings
            - task: string
        Returns: list of dictionaries containing classes, task and image content
        """
        # TODO: add tags 
        # TODO: turn into an image object
        result = self.search(class_list, task)
        img_list = []
        for i in range(len(result)):
            r = self.sdk.get_image(result[i]['preview'])
            img_list.append({'classes': result[i]['annotations']['classes'], 'task': task, 'img': BytesIO(r.content)})
        return img_list

    def search(self, class_list, task):
        """
        Given list of desired classes and an annotation task, returns a subset of the dataset by limiting images and their annotations to that classes and the annotation task.
        Args:
            - class_list: list of strings. 
                classes with the same images
            - task: str.
                annotation task
        Returns: subset of the dataset 
        """
        # TODO: add exception for the original dataset specific methods.
        result = self.sdk.search_images(class_list, task, self.id)
        filtered_dataset = deepcopy(self)

        new_img_name_list = [im.get('name') for im in result]
        filtered_dataset.images = list(filter(lambda im: im.name in new_img_name_list, self.images))
        filtered_dataset.annotations = list(
            filter(lambda annotation: annotation.get('file_name') in new_img_name_list, self.annotations))

        return filtered_dataset

    def view(self):
        self.sdk.view_dataset(self.id)

    def view_annotate(self, annotation_set_id=None):
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            annotation_set.view()

    def view_annotation_statistics(self, annotation_set_id=None):
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            annotation_set.view_stats()

    def view_image(self, image_id, cls=None, tag=None):
        self.sdk.view_image(image_id, self.id)

    def view_search(self, **kwargs):
        pass

    def view_objects(self, cls, tag):
        pass
