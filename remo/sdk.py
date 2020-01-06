import csv
from .domain import Dataset, AnnotationSet
from .api import API
from .browser import browse
from .endpoints import frontend
from .exporter import get_json_to_csv_exporter


class SDK:
    def __init__(self, server, email, password, browse=browse):
        self.api = API(server, email, password)
        self.browse=browse

    # MC: there is a problem in fetching annotation sets
    def create_dataset(self, name, local_files=[], paths_to_upload=[], urls=[], annotation_task=None):
        """ 
        Creates a new dataset in Remo and optionally populate it with images and annotation from local drive or URL

        Args:
           name: string, name of the Dataset

           local_files: list of files or directories.
                Function will scan for .png, .jpeg, .tiff and .jpg in the folders and sub-folders.

           paths_to_upload: list of files or directories.
            These files will be uploaded to the local disk.
              - files supported: image files, annotation files and archive files.
              - Annotation files: json, xml, csv. If annotation file is provided, you need to provide annotation task.
              - Archive files: zip, tar, gzip. These files are unzipped, and then we scan for images, annotations and other archives. Support for nested archive files, image and annotation files in the same format supported elsewhere

           urls: list of urls pointing to downloadable target, which should be an archive file.
              The function will download the target of the URL, scan for archive files, unpack them and the results will be scanned for images, annotations and other archives.

           annotation_task:
               object_detection = 'Object detection'. Supports Coco, Open Images, Pascal
               instance_segmentation = 'Instance segmentation'. Supports Coco
               image_classification = 'Image classification'. ImageNet


        Returns: remo Dataset
        """

        result = self.api.create_dataset(name)
        my_dataset = Dataset(self, **result)
        print(result)
        my_dataset.add_data(local_files, paths_to_upload, urls, annotation_task)
        my_dataset.initialise_images()
        my_dataset.initialize_annotation_set()
        my_dataset.initialise_annotations()
        return my_dataset

    def add_data_to_dataset(self, dataset_id, local_files=[],
                            paths_to_upload=[], urls=[], annotation_task=None, folder_id=None):
        """
        Adds data to existing dataset

        Args:
            - dataset_id: id of the desired dataset to extend (integer)
            - local_files: list of files or directories.
                    Function will scan for .png, .jpeg, .tiff and .jpg in the folders and sub-folders.
            - paths_to_upload: list of files or directories.
                    These files will be uploaded to the local disk.

               files supported: image files, annotation files and archive files.

               Annotation files: json, xml, csv.
                    If annotation file is provided, you need to provide annotation task.

               Archive files: zip, tar, gzip.
                    These files are unzipped, and then we scan for images, annotations and other archives. Support for nested archive files, image and annotation files in the same format supported elsewhere

            - urls: list of urls pointing to downloadable target, which should be an archive file.
                    The function will download the target of the URL - then we scan for archive files, unpack them and proceed as per Archive file section.

            - annotation_task:
               object_detection = 'Object detection'. Supports Coco, Open Images, Pascal
               instance_segmentation = 'Instance segmentation'. Supports Coco
               image_classification = 'Image classification'. ImageNet
            - folder_id: if there is a folder in the targer remo id, and you want to add images to a specific folder, you can specify it here.
        """
        result = {}
        if len(local_files):
            if type(local_files) is not list:
                raise ValueError(
                    'Function parameter "paths_to_add" should be a list of file or directory paths, but instead is a ' + str(
                        type(local_files)))

            files_upload_result = self.api.upload_local_files(dataset_id, local_files, annotation_task, folder_id)
            result['files_link_result'] = files_upload_result

        if len(paths_to_upload):
            if type(paths_to_upload) is not list:
                raise ValueError(
                    'Function parameter "paths_to_upload" should be a list of file or directory paths, but instead is a ' + str(
                        type(paths_to_upload)))

            files_upload_result = self.api.bulk_upload_files(dataset_id=dataset_id,
                                                             files_to_upload=paths_to_upload,
                                                             annotation_task=annotation_task,
                                                             folder_id=folder_id)

            result['files_upload_result'] = files_upload_result

        if len(urls):
            if type(urls) is not list:
                raise ValueError(
                    'Function parameter "urls" should be a list of URLs, but instead is a ' + str(type(urls)))

            urls_upload_result = self.api.upload_urls(dataset_id=dataset_id,
                                                      urls=urls,
                                                      annotation_task=annotation_task,
                                                      folder_id=folder_id)

            print(urls_upload_result)
            result['urls_upload_result'] = urls_upload_result
        return result

    def list_datasets(self):
        """
        Lists the available datasets
        Returns: dataset id and dataset name
        """
        resp = self.api.list_datasets()
        result = []
        for dataset in resp.get('results', []):
            result.append(Dataset(self, id=dataset['id'], name=dataset['name']))
        return result

    def get_dataset(self, dataset_id):
        """
        Given a dataset id returns the dataset
        Args:
            dataset_id: int
        Returns: remo dataset
        """
        result = self.api.get_dataset(dataset_id)
        dataset = Dataset(self, **result)
        dataset.initialize_annotation_set()
        dataset.initialise_annotations()
        dataset.initialise_images()
        return dataset

    def list_annotation_sets(self, dataset_id):
    #TODO test whether to hide the function
        result = self.api.list_annotation_sets(dataset_id)
        return [
            AnnotationSet(self,
                          id=annotation_set['id'],
                          name=annotation_set['name'],
                          updated_at=annotation_set['updated_at'],
                          task=annotation_set['task']['name'],
                          top3_classes=annotation_set['statistics']['top3_classes'],
                          total_images=annotation_set['statistics']['annotated_images_count'],
                          total_classes=annotation_set['statistics']['total_classes'],
                          total_annotation_objects=annotation_set['statistics']['total_annotation_objects'])
            for annotation_set in result.get('results', [])
        ]

    def get_annotation_set(self, id):
        annotation_set = self.api.get_annotation_set(id)
        return AnnotationSet(self,
                      id=annotation_set['id'],
                      name=annotation_set['name'],
                      updated_at=annotation_set['updated_at'],
                      task=annotation_set['task']['name'],
                      total_classes=len(annotation_set['classes']))


    def get_annotations(self, annotation_set_id, annotation_format='json'):
        """
        Args:
            annotation_format: can be one of ['json', 'coco'], default='json'
        Returns: annotations
        """
        result = self.api.get_annotations(annotation_set_id, annotation_format)
        return result
    
    def _list_annotation_classes(self, annotation_set_id=None):
        return self.api.list_annotation_classes(annotation_set_id)
    
    def _export_annotation_to_csv(self, annotation_set_id, output_file, dataset):
        """
        Takes annotations and saves as a .csv file
        Args:
            annotation_set_id: int
            output_file: .csv path
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        exporter = get_json_to_csv_exporter(annotation_set.task)
        if not exporter:
            print("ERROR: for giving annotation task '{}' export function not implemented".format(annotation_set.task))
            return

        annotation_results = dataset.annotations

        with open(output_file, 'w', newline='') as output:
            csv_writer = csv.writer(output)
            exporter(annotation_results, csv_writer)

    def list_dataset_images(self, dataset_id, folder_id=None, **kwargs):
        """
        Given a dataset id returns list of the dataset images
        
        Args:
            - dataset_id: the id of the dataset to query
            - folder_id: the id of the folder to query
            - **kwargs:
                Keyword Arguments:
                   - limit: int. 
                       the number of images to be listed.
        Returns: list of images with their names and ids
        """

        if folder_id:
            result = self.api.list_dataset_contents_by_folder(dataset_id, folder_id, **kwargs)
        else:
            result = self.api.list_dataset_contents(dataset_id, **kwargs)

        images = [
            {
                'id': entry.get('id'),
                'name': entry.get('name'),
            }
            for entry in result.get('results', [])
        ]
        return images

    def get_images_by_id(self, dataset_id, image_id):
        """
        Get image file by dataset_id and image_id
        Args:
            dataset_id: int
            image_id: int

        Returns: image
        """
        return self.api.get_images_by_id(dataset_id, image_id)

    def get_image(self, url):
        return self.api.get_image(url)

    def search_images(self, classes=None, task=None, dataset_id=None, limit=None):
        """
        Search images by class and annotation task
        Args:
            classes: string or list of strings.
                Name of the classes to filter dataset.
            task: string
                Name of the annotation task to filter dataset
            dataset_id: int
                Narrows search result to giving dataset
            limit: int
                Limits number of search results

        Returns: image_id, dataset_id, name, annotations
        """
        return self.api.search_images(classes, task, dataset_id, limit)

    def view_search(self, cls=None, task=None):
        """
        Opens browser in search page

        """
        self._view(frontend.search)

    def view_image(self, image_id, dataset_id):
        """
        Opens browser on the image view for giving image
        Args:
            image_id: int
            dataset_id: int
        Returns: Browse UI of the selected image
        """
        # TODO: find easier way to check if image belongs to dataset
        img_list = self.list_dataset_images(dataset_id)
        contain = False
        for img_dict in img_list:
            if image_id == img_dict['id']:
                contain = True
                self._view(frontend.image_view.format(image_id, dataset_id))
        if not contain:
            msg = 'Image ID: %s' % str(image_id) + ' not in dataset %s' % str(dataset_id)
            print(msg)
   
    def open_ui(self):
        """
        Opens the main page of Remo
        """
        self._view(frontend.datasets)

    def view_dataset(self, id):
        """
        Opens browser for the given dataset
        Args:
            id: int
                dataset id
        Returns: Browse UI of the selected dataset
        """
        self._view(frontend.datasets, id)

    def view_annotation_set(self, id):
        """
        Opens browser in annotation view for the given annotation set
        Args:
            id: int
               annotation set id
        Returns: Browse UI of the selected annotation set
        """
        self._view(frontend.annotation, id)

    def view_annotation_stats(self, annotation_set_id):
        """
        Opens browser in annotation statistics view for the given annotation set
        Args:
            id: int
               annotation set id
        Returns: Browse UI for the statistics of the selected annotation set
        """
        self._view(frontend.annotation_detail.format(annotation_set_id))

    def _view(self, url, *args, **kwargs):
        self.browse(self.api.url(url, *args, **kwargs))
