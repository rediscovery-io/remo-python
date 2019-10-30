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
        #print(id, dataset,path_to_image, '\n')
    
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
            
    def annotation_sets(self):
        return self.sdk.annotation_sets(self.id)
        
    def initialise_images(self):
        list_of_images = self.list_images()
        for i_image in list_of_images:
            my_image = Image(id = None, path = i_image, dataset = self.name)
            print(i_image, self.name)
            self.images.append(my_image)
    
    def list_images(self, folder_id = None, **kwargs):
        return self.sdk.list_dataset_images(self.id, folder_id = None, **kwargs)

    def add_data(self, local_files=[], paths_to_upload = [], urls=[], annotation_task=None, folder_id=None):
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

            
        return self.sdk.add_data_to_dataset(dataset_id = self.id,
                                            local_files= local_files,
                                            paths_to_upload = paths_to_upload,
                                            urls = urls,
                                            annotation_task = annotation_task,
                                            folder_id = folder_id)

    def fetch(self):
        dataset = self.sdk.get_dataset(self.id)
        self.__dict__.update(dataset.__dict__)

    def browse(self):
        utils.browse(self.sdk.ui.dataset_url(self.id))
        
    def browse_ann(self, ann_id):
        utils.browse(self.sdk.ui.annotate_url(ann_id))

    def annotate(self):
        # TODO: select by annotation task
        print(self._annotation_sets)
        if len(self._annotation_sets) > 0:
            utils.browse(self.sdk.ui.annotate_url(self._annotation_sets[0]))
        else:
            print("No annotation sets in dataset " + self.name)



    def search(self, **kwargs):
        pass
        
        
    def get_images(self, cls=None, tag=None):
        # TODO: add class and tags 
        dataset_details = self.sdk.all_info_datasets() 
        dataset_info = None
        for res in dataset_details['results']:
            if res['id'] == self.id:
                dataset_info = res
        url_list = []
        image_thumbnails = dataset_info.get('image_thumbnails')
        for i in range(len(image_thumbnails)):
            url_ = image_thumbnails[i]['image']
            url_list.append(url_)
        return url_list
    
    def show_images(self, cls=None, tag=None):
        # TODO: redirect to ui with endpoints
        image_urls = self.get_images(cls=None, tag=None)
        imgs = []
        for url in image_urls:
            bytes_ = requests.get(url).content
            rawIO = BytesIO(bytes_)
            imgs.append(rawIO)
        return imgs
  
    
    def show_objects(self, cls, tag):
        pass
        

 