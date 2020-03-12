
from typing import List


class AnnotationObject:
        """
        Represents a single annotation object. This can be:
        
        - list of classes only: to assign classes to an image for image classification tasks
        - bounding box and list of classes: to create a bounding box annotation object and assign it a list of classes
        - segment and list of classes: to create a polygon annotation object and assign it a list of classes

        Args:
            xmin: X min
            ymin: Y min
            xmax: X max
            ymax: Y max
            
        Examples:
            to create a bounding box:
                annotation_obj = AnnotationObject('image.png', 'Dog')
                annotation_obj.bbox = [1, 23, 3, 2]
                
            to create a polygon:
                annotation_obj = AnnotationObject('image.png', 'Dog')
                annotation_obj.segment = [1, 23, 3, 2, 1, 2, 1, 2]
        """

    
    def __init__(self, img_filename: str, classes, object=None):
        if object and (not
                       isinstance(object, AnnotationObject.Bbox) and not isinstance(object, AnnotationObject.Segment)):
            raise Exception('Expected object type AnnotationObject.Bbox or AnnotationObject.Segment')

        self.filename = img_filename
        self.classes = classes if isinstance(classes, list) else [classes]
        self.object = object

    @property
    def task(self):
        if not self.object:
            return 'image_classification'
        return self.object.task

    @property
    def bbox(self):
        if isinstance(self.object, AnnotationObject.Bbox):
            return self.object
        return None

    @bbox.setter
    def bbox(self, values: List[int]):
        if len(values) != 4:
            raise Exception('Boundind box expected 4 values: xmin, ymin, xmax, ymax')

        xmin, ymin, xmax, ymax = values
        self.object = AnnotationObject.Bbox(xmin, ymin, xmax, ymax)


    @property
    def segment(self):
        if isinstance(self.object, AnnotationObject.Segment):
            return self.object
        return None

    @segment.setter
    def segment(self, points: List[int]):
        if not points:
            raise Exception('Segment coordinates cannot be an empty list.')
        if len(points) % 2 == 1:
            raise Exception('Segment coordinates need to be an even number of elements indicating (x,y) coordinates of each point.')
        self.object = AnnotationObject.Segment(points)


    class Bbox:
        """
        Represents coordinates of a bounding box annotation. Used in object detection.

        Args:
            xmin: X min
            ymin: Y min
            xmax: X max
            ymax: Y max
        """
        task = 'object_detection'

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
        task = 'instance_segmentation'

        def __init__(self, points: List[int]):
            self.points = [{'x': x, 'y': y} for x, y in zip(points[::2], points[1::2])]



if __name__ == '__main__':
    annotation_obj = AnnotationObject('image.png', 'Dog')
    annotation_obj.bbox = [1, 23, 3, 2]
    
    annotation_obj.segment = [1, 23, 3, 2, 1, 2, 1, 2]
    print('Task:', annotation_obj.task)
    print('-' * 50)

    annotation_obj.bbox = [1, 23, 3, 2]
    print('Task:', annotation_obj.task)
    print('bbox:', annotation_obj.bbox)
    print('-' * 50)

    annotation_obj.segment = [1, 23, 3, 2, 1, 2, 1, 2]
    print('Task:', annotation_obj.task)
    print('bbox:', annotation_obj.bbox)
    print('segment:', annotation_obj.segment)




