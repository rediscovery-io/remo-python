from typing import List
from .task import *

class Annotation:
    """
    Represents a single annotation object. This can be:

    - list of classes only: to assign classes to an image for image classification tasks
    - bounding box and list of classes: to create a bounding box annotation object and assign it a list of classes
    - segment and list of classes: to create a polygon annotation object and assign it a list of classes

    Args:
        img_filename: file name of the image the annotation refers to
        classes: class or list of classes to add to the whole image or the object
        object: the specific annotation object to add

    Examples:
        to create a bounding box:
            annotation = Annotation('image.png', 'Dog')
            annotation.bbox = [1, 23, 3, 2]

        to create a polygon:
            annotation = Annotation('image.png', 'Dog')
            annotation.segment = [1, 23, 3, 2, 1, 2, 1, 2]
    """

    def __init__(self, img_filename: str = None, classes=None, object=None):
        if object and (
            not isinstance(object, Annotation.Bbox) and not isinstance(object, Annotation.Segment)
        ):
            raise Exception('Expected object type Annotation.Bbox or Annotation.Segment')

        self.img_filename = img_filename
        self.classes = classes if isinstance(classes, list) else [classes]
        self.object = object
        self.coordinates = None
        self.type = None
        
    def __str__(self):
        my_representation =  "Annotation: {classes} (type:{ann_type}, file:{filename})".format(classes=self.classes, ann_type=self.type, filename=self.img_filename) 
        
        return my_representation

    def __repr__(self):
        return self.__str__()

    @property
    def task(self):
        if not self.object:
            return image_classification
        return self.object.task

    @property
    def bbox(self):
        if isinstance(self.object, Annotation.Bbox):
            return self.object
        return None

    @bbox.setter
    def bbox(self, values: List[int]):
        if len(values) != 4:
            raise Exception('Bounding box expects 4 values: xmin, ymin, xmax, ymax')

        self.object = Annotation.Bbox(*values)
        self.coordinates = values
        self.type = 'Bounding Box'
        
    @property
    def segment(self):
        if isinstance(self.object, Annotation.Segment):
            return self.object
        return None

    @segment.setter
    def segment(self, points: List[int]):
        if not points:
            raise Exception('Segment coordinates cannot be an empty list.')
        if len(points) % 2 == 1:
            raise Exception(
                'Segment coordinates need to be an even number of elements indicating (x, y) coordinates of each point.'
            )
        self.object = Annotation.Segment(points)
        self.coordinates = points
        self.type = 'Polygon'
        
    
    class Bbox:
        """
        Represents coordinates of a bounding box annotation. Used in object detection.

        Args:
            xmin: X min
            ymin: Y min
            xmax: X max
            ymax: Y max
        """
        task = object_detection

        def __init__(self, xmin: int, ymin: int, xmax: int, ymax: int):
            self.xmin = xmin
            self.ymin = ymin
            self.xmax = xmax
            self.ymax = ymax

    class Segment:
        """
        Represents coordinates of a segment annotation. Used in instance segmentation.

        Args:
            points: list of segment coordinates ``[x0, y0, x1, y1, ..., xN, yN]``
        """

        task = instance_segmentation

        def __init__(self, points: List[int]):
            self.points = [{'x': x, 'y': y} for x, y in zip(points[::2], points[1::2])]
