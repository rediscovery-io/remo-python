import csv
import os
import tempfile
from typing import List, TypeVar
from .domain.task import *

Annotation = TypeVar('Annotation')


def check_annotation_task(expected_task, actual_task):
    if expected_task is not actual_task:
        raise Exception(
            "Expected annotation task '{}', but received annotation for '{}'".format(
                expected_task, actual_task
            )
        )


class SimpleCSVBase:
    task = None
    headers = None

    @staticmethod
    def inline_classes(classes):
        if isinstance(classes, list):
            return ';'.join(classes)
        if isinstance(classes, str):
            return classes
        return ''

    def validate_annotation_task(self, annotations: List[Annotation]):
        for annotation in annotations:
            check_annotation_task(self.task, annotation.task)

    def prepare_data(self, annotations: List[Annotation]) -> List[List[str]]:
        self.validate_annotation_task(annotations)
        return [self.headers, *self._csv_data(annotations)]

    def _csv_data(self, annotations: List[Annotation]) -> List[List[str]]:
        return []


class SimpleCSVForObjectDetection(SimpleCSVBase):
    task = object_detection
    headers = ["file_name", "class_name", "xmin", "ymin", "xmax", "ymax"]

    def _csv_data(self, annotations: List[Annotation]) -> List[List[str]]:
        return [
            [annotation.img_filename,  self.inline_classes(annotation.classes), *annotation.coordinates]
            for annotation in annotations
        ]


class SimpleCSVForInstanceSegmentation(SimpleCSVBase):
    task = instance_segmentation
    headers = ["file_name", "class_name", "coordinates"]

    @staticmethod
    def inline_coordinates(coordinates):
        return '; '.join(map(str, coordinates))

    def _csv_data(self, annotations: List[Annotation]) -> List[List[str]]:
        return [
            [
                annotation.img_filename,
                self.inline_classes(annotation.classes),
                self.inline_coordinates(annotation.coordinates),
            ]
            for annotation in annotations
        ]


class SimpleCSVForImageClassification(SimpleCSVBase):
    task = image_classification
    headers = ["file_name", "class_name"]

    def _csv_data(self, annotations: List[Annotation]) -> List[List[str]]:
        return [[annotation.img_filename, self.inline_classes(annotation.classes)] for annotation in annotations]


csv_makers = {
    SimpleCSVForObjectDetection.task: SimpleCSVForObjectDetection(),
    SimpleCSVForInstanceSegmentation.task: SimpleCSVForInstanceSegmentation(),
    SimpleCSVForImageClassification.task: SimpleCSVForImageClassification()
}


def prepare_annotations_for_upload(annotations: List[Annotation], annotation_task):
    csv_maker = csv_makers.get(annotation_task)
    if not csv_maker:
        raise Exception(
            "Annotation task '{}' not recognised. "
            "Supported annotation tasks are 'instance_segmentation', 'object_detection' and "
            "'image_classification'".format(annotation_task)
        )

    return csv_maker.prepare_data(annotations)


def create_tempfile(annotations: List[Annotation]) -> (str, List[str]):
    fd, temp_path = tempfile.mkstemp(suffix='.csv')

    annotation_task = annotations[0].task
    prepared_data = prepare_annotations_for_upload(annotations, annotation_task)

    # getting a list of classes. Skipping the first row as it contains the csv header
    list_of_classes = [row[1] for row in prepared_data[1:]]

    classes = set()
    if isinstance(list_of_classes, list) and list_of_classes:
        for item in list_of_classes:
            if isinstance(item, list):
                classes.union(item)
            else:
                classes.add(item)

    list_of_classes = list(classes)

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
