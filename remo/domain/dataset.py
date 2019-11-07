from io import BytesIO


class Image:
    """
    TODO: Start using it
    WIP
    """
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
    def __init__(self, sdk, **kwargs):
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
        """
        Returns a list of the annotation sets within the dataset
        """

        return self.sdk.list_annotation_sets(self.id)

    def annotation_statistics(self):
        """
        Prints annotation statistics of the dataset
        TODO - for which annotation set?
        WIP
        
        """
        return self.sdk.annotation_statistics(self.id)

    def initialise_images(self):
        list_of_images = self.list_images()
        for i_image in list_of_images:
            my_image = Image(id=None, path=i_image, dataset=self.name)
            self.images.append(my_image)

    def list_images(self, folder_id=None, **kwargs):
        """
        Prints annotation statistics of the dataset
        TODO - for which annotation set?
        WIP
        
        """
        return self.sdk.list_dataset_images(self.id, folder_id=None, **kwargs)

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

    def view(self):
        self.sdk.view_dataset(self.id)

    def view_annotation(self, annotation_set_id):
        # TODO: select by annotation task
        self.sdk.view_annotation_set(annotation_set_id)

    def view_annotation_statistics(self, ann_id):
        self.sdk.view_annotation_stats(ann_id)

    def get_images(self, image_id, cls=None, tag=None):
        # TODO: add class and tags & multiple images
        r = self.sdk.get_images(self.id, image_id)
        return BytesIO(r.content)

    def view_image(self, image_id, cls=None, tag=None):
        return self.sdk.view_image(image_id, self.id)

    def view_search(self, **kwargs):
        pass

    def view_objects(self, cls, tag):
        pass
