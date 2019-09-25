from enum import Enum


class AnnotationTask(Enum):
    object_detection = 'Object detection'
    instance_segmentation = 'Instance segmentation'
    image_classification = 'Image classification'
