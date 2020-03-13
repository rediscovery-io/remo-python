import csv
import os
import tempfile
from typing import List

from remo.domain import Annotation                                


def prepare_annotations_for_upload(annotations: List[Annotation], annotation_task):
    
    my_objects_list = []
    
    
    if annotation_task is 'object_detection':
        my_objects_list.append(["file_name","class_name","xmin","ymin","xmax","ymax"])
        
    elif annotation_task is 'instance_segmentation':
        my_objects_list.append(["file_name","class_name","coordinates"])
        
    elif annotation_task is 'image_classification':
        my_objects_list.append(["file_name","class_name"])
        
    else:
        raise Exception("Annotation task {} not recognised. Supported annotation tasks are 'instance_segmentation', 'object_detection' and 'image_classification'".format(annotation_task))
    
    for i_annotation in annotations:
        
        if i_annotation.task is not annotation_task:
            raise Exception("Expected annotation task {}, but received some annotation for {}".format(annotation_task,i_annotation.task))
            
        my_inner_list = []
        # file name
        my_inner_list.append(i_annotation.img_filename)
        
        # classes
        my_inner_list.append(i_annotation.classes)
        
        # coordinates
        if annotation_task is 'object_detection':
            my_inner_list.extend(i_annotation.coordinates)
            
        elif annotation_task is 'instance_segmentation':
            my_inner_list.append['; '.join(map(str, i_annotation.coordinates))]
            
        my_objects_list.append(my_inner_list)

    return my_objects_list
    
    
def create_tempfile(annotations: List[Annotation]) -> str:
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    
    annotation_task = annotations[0].task
    prepared_data = prepare_annotations_for_upload(annotations, annotation_task)
    
    with os.fdopen(fd, 'w') as temp:
        writer = csv.writer(temp)
        writer.writerows(prepared_data)
            
    return temp_path


def parse_csv_obj_det(file_path) -> List[Annotation]:
    """
    Args
        file_path: path to annotations


    Example:
    # file_name,class_name,coordinates
    # ILSVRC2012_val_00000003.JPEG,N01751748, 10 20 30 40
    # ILSVRC2012_val_00000003.JPEG,N01751748, 10 20 30 40


    Returns:
        List[:class:`remo.Annotation`]
    """

    annotations = []

    with open(file_path, 'r') as f:
        csv_file = csv.reader(f, delimiter=',')
        for row in csv_file:
            file_name, class_name, coordinates = row
            # convert coordinates to list of integers
            bbox = [int(val) for val in coordinates.split(' ')]

            annotation = Annotation(img_filename=file_name, classes=class_name)
            annotation.bbox = bbox

            annotations.append(annotation)
    return annotations
