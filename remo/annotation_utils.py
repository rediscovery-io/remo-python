import csv

from remo.domain import Annotation


def parse_csv_obj_det(file_path):
    """
    Args
        file_path: path to annotations


    Example:
    # file_name,class_name,coordinates
    # ILSVRC2012_val_00000003.JPEG,N01751748, 10 20 30 40
    # ILSVRC2012_val_00000003.JPEG,N01751748, 10 20 30 40


    :return: annotations
    """

    annotations = []

    with open(file_path, 'r') as f:
        csv_file = csv.reader(f, delimiter=',')
        for row in csv_file:
            file_name, class_name, coordinates = row
            # convert coordinates to list of integers
            bbox = [int(val) for val in coordinates.split(' ')]

            annotation = Annotation(img_filename=file_name)
            annotation.add_item(classes=[class_name], bbox=bbox)
            annotations.append(annotation)

    return annotations
