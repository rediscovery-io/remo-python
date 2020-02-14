import csv

# file_name,class_name,coordinates
# ILSVRC2012_val_00000003.JPEG,N01751748, 10 20 30 40
from remo.domain import Annotation


def parse_plain_csv_object_detection(file_path):
    """
    Args
        file_path: path to annotations

    :return: annotations
    """

    annotations = []

    with open(file_path, 'r') as f:
        csv_file = csv.reader(f, delimiter=',')
        for row in csv_file:
            file_name = row[0].strip()
            class_name = row[1].strip()
            bbox = list(map(int, row[2].split()))

            annotation = Annotation(file_name=file_name)
            annotation.add_item(classes=[class_name], bbox=bbox)
            annotations.append(annotation)

    return annotations
