import csv
import os
import tempfile
from typing import List

from remo.domain import Annotation                                


def create_tempfile(annotations: List[Annotation]) -> str:
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w') as temp:
        writer = csv.writer(temp)
        writer.writerow(annotations[0].csv_columns())
        for annotation in annotations:
            writer.writerows(annotation.csv_rows())
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
