import csv
from typing import List

from remo.domain import Annotation                                
                                               

def prepare_annotations_for_upload(annotations: List[Annotation]) -> List:
   
    my_objects_list = []
    for i_annotation in annotations:

        my_inner_list = []
        my_inner_list.append(i_annotation.img_filename)
        my_inner_list.append(i_annotation.classes)
        my_inner_list.extend(i_annotation.coordinates)
        my_objects_list.append(my_inner_list)
    
    return my_objects_list
    
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
