import csv
import os
import tempfile
from typing import List, TypeVar
from .domain.task import *

Annotation = TypeVar('Annotation')

def check_annotation_task(expected_task, actual_task):
    if expected_task is not actual_task:
        raise Exception("Expected annotation task '{}', but received annotation for '{}'".format(expected_task,actual_task))
            
def prepare_annotations_for_upload(annotations: List[Annotation], annotation_task):
    
    my_objects_list = []
    
    
    if annotation_task is object_detection:
        
        my_objects_list.append(["file_name","class_name","xmin","ymin","xmax","ymax"])

        for i_annotation in annotations:
            check_annotation_task(annotation_task, i_annotation.task)

            my_inner_list = []
            my_inner_list.append(i_annotation.img_filename)
            my_inner_list.append(i_annotation.classes)
            my_inner_list.extend(i_annotation.coordinates)
            my_objects_list.append(my_inner_list)
        
    elif annotation_task is instance_segmentation:
        
        my_objects_list.append(["file_name","class_name","coordinates"])
        
        for i_annotation in annotations:
            
            check_annotation_task(annotation_task, i_annotation.task)

            my_inner_list = []
            my_inner_list.append(i_annotation.img_filename)
            my_inner_list.append(i_annotation.classes)
            my_inner_list.append['; '.join(map(str, i_annotation.coordinates))]          
            my_objects_list.append(my_inner_list)
        
        
    elif annotation_task is image_classification:
        my_objects_list.append(["file_name","class_name"])
        
        for i_annotation in annotations:
            
            check_annotation_task(annotation_task, i_annotation.task)

            my_inner_list = []
            my_inner_list.append(i_annotation.img_filename)
            my_inner_list.append(i_annotation.classes)
            my_objects_list.append(my_inner_list)

    else:
        raise Exception("Annotation task '{}' not recognised. Supported annotation tasks are 'instance_segmentation', 'object_detection' and 'image_classification'".format(annotation_task))

    return my_objects_list
    
def create_tempfile(annotations: List[Annotation]) -> str:
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    
    annotation_task = annotations[0].task
    prepared_data = prepare_annotations_for_upload(annotations, annotation_task)
    
    # getting a list of classes. Skipping the first row as it contains the csv header
    list_of_classes = [row[1] for row in prepared_data[1:]]
    list_of_classes = list(set(list_of_classes))
    
    with os.fdopen(fd, 'w') as temp:
        writer = csv.writer(temp)
        writer.writerows(prepared_data)
            
    return temp_path, list_of_classes


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
