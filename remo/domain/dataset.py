from io import BytesIO
from .image import Image
from copy import deepcopy
import csv


class Dataset:
    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.images = []
        self.annotation_sets = []
        self.default_annotation_set = None
        self.annotations = []
        self.images_dict = {}
        # self.original = True

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

    def get_annotations(self, annotation_set_id=None, annotation_format='json'):
        """
        Get annotation of the dataset
        
        Args:
            - annotation_set_id: int default: default_annotation_set
            - annotation_format: string. can be one of ['json', 'coco'], default='json'

        Returns: file_name, height, width, tags, task, annotations with classes and coordinates
        """
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.get_annotations(annotation_format)

        print('ERROR: annotation set not defined')

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
            self.add_data(paths_to_upload=[path_to_annotation_file], annotation_task=annotation_task, annotation_set_id=annotation_set.id)
            annotation_set = self.sdk.get_annotation_set(annotation_set.id)
        return annotation_set

    # def upload_annotations(self, path, task):
    #    return self.sdk.upload_annotations(self.id, path, task)

    def add_annotation(self, image_name, annotation_set_id, cls, coordinates=None, object_id=None):
        """
        Adds annotations to the specified annotation set
        Args:
           
            - image_name: str.
                file name of the image
            - annotation_set_id: int.
                the id of the annotation set 
            - cls: str. 
                class of the detected object
            - coordinates: list. Default None.
                list of dictionaries containing coordinates of the annotations.
            - object_id: int. Default None.
                id of the object in the given image. If not feed any value considered as Image classification task. 
        """

        image_id = self.images_dict.get(image_name)
        return self.sdk.add_annotation(self.id, annotation_set_id, image_id, cls, coordinates, object_id)

    def add_annotations_by_csv(self, path_to_annotation_file, annotation_set_id):
        # WARNING: this function doesn't work as expected
        """
        Gets annotations in a csv format and adds annotations line by line.  
        Args:
           
            - path_to_annotation_file: str. 
                path to the .csv file of the annotations. 
                annotations are in the format given below:
                    Object detection: file_name, class, xmin, ymin, xmax, ymax
                    Image classification: file_name, class
            - annotation_set_id: int.
           
        """
        self._initialize_images_dict()

        with open(path_to_annotation_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            headers = next(csv_reader, None)
            # Initialize object counter 
            object_id = 0
            # We initialize img_name with null and then assign file_name in each row
            # Each iteration, we compare if we pass a new image in order to reset object counters
            img_name = ''
            for row in csv_reader:
                cls = row[1]
                if len(headers) > 5:
                    # It's object detection
                    if row[0] != img_name:
                        # Reset the object counter at a new image
                        object_id = 0
                    img_name = row[0]
                    coordinates = row[2:]
                    self.add_annotation(img_name, annotation_set_id, cls, coordinates, object_id)
                    object_id += 1
                else:
                    # It's image classification
                    img_name = row[0]
                    self.add_annotation(img_name, annotation_set_id, cls)
        # fetch the dataset 
        self.fetch()

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
        num_images = len(self.annotations)
        images = self.list_images(limit=num_images)
        # images = self.list_images()
        self.images = [
            Image(id=img.get('id'), path=img, dataset=self.name, name=img.get('name'))
            for img in images
        ]

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
            self.annotations = self.get_annotations(annotation_set.id)

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
        if limit:
            return self.sdk.list_dataset_images(self.id, folder_id, limit=limit)
        else:
            return self.sdk.list_dataset_images(self.id, folder_id, limit=len(self.annotations))

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

    def _initialize_images_dict(self):
        for item in self.images:
            self.images_dict[item.name] = item.id

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
