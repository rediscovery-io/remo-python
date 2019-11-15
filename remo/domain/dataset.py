from io import BytesIO
import csv
import remo.domain.task as t

class AnnotationSet:
    def __init__(self, api, **kwargs):
        self.api = api
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.task = kwargs.get('task')
        self.total_classes = kwargs.get('total_classes')
        self.released_at = kwargs.get('released_at')
        self.updated_at = kwargs.get('updated_at')
        self.total_images = kwargs.get('total_images')
        self.top3_classes = kwargs.get('top3_classes')
        self.total_annotation_objects = kwargs.get('total_annotation_objects')

    def __str__(self):
        return "Annotation set {id} - '{name}', task: {task}, #classes: {total_classes}".format(
            id=self.id, name=self.name, task=self.task, total_classes=self.total_classes)

    def __repr__(self):
        return self.__str__()

    def get_annotations(self, annotation_set_id=None, annotation_format='json'):
        """
        :param annotation_format: choose format from this list ['json', 'coco']
        :return: annotations
        """
        ann_id = annotation_set_id or self.id        
        resp = self.api.get_annotations(ann_id, annotation_format)
        return resp
    
    def export_annotation_to_csv(self, annotation_set_id, output_file, task):
        """
        Takes annotations and saves as a .csv file  
        Args:
            annotation_set_id: int
            output_file: .csv path
            annotation_task:
               object_detection = 'Object detection'. Supports Coco, Open Images, Pascal
               instance_segmentation = 'Instance segmentation'. Supports Coco
               image_classification = 'Image classification'. ImageNet
        """
        annotation = self.api.get_annotations(annotation_set_id, annotation_format='json')
        output = open(output_file, 'w', newline='')
        f = csv.writer(output)
        if task == t.object_detection:
            header = ['file_name', 'class', 'xmin', 'ymin', 'xmax', 'ymax']
            f.writerow(header)
            for item in annotation:
                annotations = item['annotations']
                for annotation in annotations:
                    classes = annotation['classes']
                    for cls in classes:
                        f.writerow([item['file_name'], cls] + list(annotation['bbox'].values()))
        elif task == t.instance_segmentation:
            header = ['file_name', 'class', 'coordinates']
            f.writerow(header)
            for item in annotation:
                annotations = item['annotations']
                for annotation in annotations:
                    classes = annotation['classes']
                    for cls in classes:
                        segments = ' '.join(str(v) for d in annotation['segments'] for k, v in d.items())
                        f.writerow([item['file_name'], cls, segments])
        else:
            # else it is image_classification
            header = ['file_name', 'class']
            f.writerow(header)
            for item in annotation:
                classes = item['classes']
                for cls in classes:
                    f.writerow([item['file_name'], cls])
        output.close()


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
    def __init__(self, sdk, api, **kwargs):
        self.sdk = sdk
        self.api = api
        self.annotation_set = AnnotationSet(self.api)
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.images = []
        self.annotation_sets_list = []
        self._annotation_sets = kwargs.get('annotation_sets')
        self.default_annotation_set = next(iter(self._annotation_sets or []), None)

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
        resp = self.api.list_annotation_sets(self.id)
        result = []
        for annotation_set in resp.get('results', []):
            result.append(AnnotationSet(self,
                          id=annotation_set['id'],
                          name=annotation_set['name'],
                          task=annotation_set['task']['name'],
                          total_classes=annotation_set['statistics']['total_classes'])
                         )
            
        return result

    
    def get_annotations(self, annotation_set_id=None, annotation_format='json'):
        """
        Get annotation of the dataset
        
        Args:
            - annotation_set_id: int default: default_annotation_set
            - annotation_format: string. can be one of ['json', 'coco'], default='json'

        Returns: file_name, height, width, tags, task, annotations with classes and coordinates
        """
        ann_id = annotation_set_id or self.default_annotation_set
        return self.annotation_set.get_annotations(annotation_set_id=ann_id, annotation_format='json')

    def get_annotation_statistics(self):
        """
        Prints annotation statistics of all the avaiable annotation sets of the dataset
        Returns: annotation set id, name, num of images, num of classes, num of objects, top3 classes, release and update dates
        """
        statistics = []
        for ann_set in self.annotation_sets_list:
            stat =  "Annotation set {}, name: {},  #images: {}, #classes: {}, #objects: {}, Top3 classes: {}, Released: {}, Updated {}".format(ann_set.id, ann_set.name, ann_set.total_images, ann_set.total_classes, ann_set.total_annotation_objects, ann_set.top3_classes, ann_set.released_at, ann_set.updated_at)
            statistics.append(stat)
        return statistics
    
    def export_annotation_to_csv(self, output_file, task, annotation_set_id=None):
        ann_id = annotation_set_id or self.default_annotation_set
        return self.annotation_set.export_annotation_to_csv(ann_id, output_file, task)
        
    def set_default_annotations(self, annotation_set_id):
        self.default_annotation_set = annotation_set_id
    
    def initialise_images(self):
        list_of_images = self.list_images()
        for i_image in list_of_images:
            my_image = Image(id=None, path=i_image, dataset=self.name)
            self.images.append(my_image)
            
    def initialize_annotation_set(self):
        list_of_ann_sets = self.api.list_annotation_sets(self.id)
        for i_annotation in list_of_ann_sets.get('results', []):
            my_annotation = AnnotationSet(self, id = i_annotation.get('id'),
                                          name = i_annotation.get('name'), 
                                          task = i_annotation.get('task'),
                                          total_annotation_objects = i_annotation.get('total_annotation_objects'),
                                          total_classes = i_annotation.get('total_classes'),
                                          released_at = i_annotation.get('released_at'),
                                          updated_at = i_annotation.get('updated_at'),
                                          total_images = i_annotation.get('total_images'),
                                          top3_classes = i_annotation.get('top3_classes'))
            self.annotation_sets_list.append(my_annotation)
        
    def list_images(self, folder_id=None, **kwargs):
        """
        Prints annotation statistics of the dataset
        TODO - for which annotation set?
        WIP
        
        """
        return self.sdk.list_dataset_images(self.id, folder_id=None, **kwargs)
    
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
            r = self.api.get_images_by_search(result[i]['preview'])
            img_list.append({'classes':result[i]['annotations']['classes'], 'task': task, 'img':BytesIO(r.content)})
        return img_list
    
    def search_images(self, class_list, task):
        # TODO: convert result into list of dataset objects
        return self.sdk.search_images(class_list, task, self.id)    
    
    def view(self):
        self.sdk.view_dataset(self.id)

    def view_annotate(self, annotation_set_id=None):
        # TODO: select by annotation task
        ann_id = annotation_set_id or self.default_annotation_set
        return self.sdk.view_annotation_set(ann_id)

    def view_annotation_statistics(self, annotation_set_id=None):
        ann_id = annotation_set_id or self.default_annotation_set
        return self.sdk.view_annotation_stats(ann_id)
    
    def view_image(self, image_id, cls=None, tag=None):
        return self.sdk.view_image(image_id, self.id)

    def view_search(self, **kwargs):
        pass

    def view_objects(self, cls, tag):
        pass
