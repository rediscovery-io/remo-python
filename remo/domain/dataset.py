from io import BytesIO

from .image import Image


class Dataset:
    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.images = []
        self.annotation_sets = []
        self.default_annotation_set = None

    def __str__(self):
        return "Dataset {id} - '{name}'".format(id=self.id, name=self.name)

    def __repr__(self):
        return self.__str__()

    def add_data(self, local_files=[], paths_to_upload=[], urls=[], annotation_task=None, folder_id=None):
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
            - folder_id: if there is a folder in the targer remo id, and you want to add images to a specific folder, you can specify it here.
        """

        return self.sdk.add_data_to_dataset(dataset_id=self.id,
                                            local_files=local_files,
                                            paths_to_upload=paths_to_upload,
                                            urls=urls,
                                            annotation_task=annotation_task,
                                            folder_id=folder_id)

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

    def _get_annotation_set(self, id):
        for annotation_set in self.annotation_sets:
            if annotation_set.id == id:
                return annotation_set

        print('ERROR: annotation set with id={} was not found'.format(id))

    def _get_annotation_set_or_default(self, annotation_set_id=None):
        if not annotation_set_id:
            return self.default_annotation_set

        return self._get_annotation_set(annotation_set_id)

    def get_annotation_statistics(self, annotation_set_id = None):
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
                stat['last_modified_date']= ann_set.updated_at
            
                statistics.append(stat)
        return statistics

    
    def export_annotation_to_csv(self, output_file, annotation_set_id=None):
        annotation_set = self._get_annotation_set_or_default(annotation_set_id)
        if annotation_set:
            return annotation_set.export_annotation_to_csv(output_file)

        print('ERROR: annotation set not defined')

    def set_default_annotations(self, annotation_set_id):
        self.default_annotation_set = self._get_annotation_set(annotation_set_id)

    def initialise_images(self):
        images = self.list_images()
        self.images = [
            Image(id=None, path=img, dataset=self.name)
            for img in images
        ]

    def initialize_annotation_set(self):
        self.annotation_sets = self.sdk.list_annotation_sets(self.id)
        if self.annotation_sets:
            self.default_annotation_set = self.annotation_sets[0]

    def list_images(self, folder_id=None, **kwargs):
        """
        Given a dataset id returns list of the dataset images

        Args:
            - dataset_id: the id of the dataset to query
            - folder_id: the id of the folder to query
        Returns: list of images with their names and ids
        """
        return self.sdk.list_dataset_images(self.id, folder_id=folder_id, **kwargs)

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
        result = self.search_images(class_list, task)
        img_list = []
        for i in range(len(result)):
            r = self.sdk.get_image(result[i]['preview'])
            img_list.append({'classes': result[i]['annotations']['classes'], 'task': task, 'img': BytesIO(r.content)})
        return img_list

    def search_images(self, class_list, task):
        # TODO: convert result into list of dataset objects
        return self.sdk.search_images(class_list, task, self.id)

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
