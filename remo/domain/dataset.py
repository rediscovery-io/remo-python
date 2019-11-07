from .interfaces import ISDK
from .. import utils
from io import BytesIO
import requests


class Image:
    id = None
    dataset = None
    path_to_image = None
    annotation_sets = []

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.dataset = kwargs.get('dataset')
        self.path_to_image = kwargs.get('path')
        # print(id, dataset,path_to_image, '\n')


class Dataset:
    def __init__(self, sdk: ISDK, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.images = []
        self._annotation_sets = []
        self.default_annotation_set = None

    def __str__(self):
        return "Dataset {id} - '{name}'".format(id=self.id, name=self.name)

    def __repr__(self):
        return self.__str__()
    
    def add_data(self, local_files=[], paths_to_upload=[], urls=[], annotation_task=None, folder_id=None):
        """
        Adds images and optionally annotations to a Dataset

        Longer Description

        Args:
            files: 
            urls: 
            annotation_task: 
            folder_id:

        Returns:


        Raises:

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

    def annotation_sets(self):
        return self.sdk.list_annotation_sets(self.id)
    
    def annotation_statistics(self):
        return self.sdk.annotation_statistics(self.id)
    
    def view_annotate(self, ann_id):
        # TODO: select by annotation task
        utils.browse(self.sdk.ui.annotate_url(ann_id))
        
    def view_annotation_statistics(self, ann_id):
        utils.browse(self.sdk.ui.annotation_stats(ann_id))

    def initialise_images(self):
        list_of_images = self.list_images()
        for i_image in list_of_images:
            my_image = Image(id=None, path=i_image, dataset=self.name)
            self.images.append(my_image)

    def list_images(self, folder_id=None, **kwargs):
        return self.sdk.list_dataset_images(self.id, folder_id=None, **kwargs)
    
    def get_images(self, image_id, cls=None, tag=None):       
        # TODO: add class and tags & multiple images
        r = self.sdk.get_images(self.id, image_id)
        return BytesIO(r.content)     
    
    def view_image(self, image_id, cls=None, tag=None):
        return self.sdk.view_image(image_id, self.id)
  
    def view(self):
        utils.browse(self.sdk.ui.dataset_url(self.id))
        
    def view_search(self, **kwargs):
        pass
    
    def view_objects(self, cls, tag):
        pass
        
