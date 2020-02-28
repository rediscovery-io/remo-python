from typing import List


class Annotation:
    """
    Represents image annotations

    Args:
        img_filename: image file name
        status: can be ``not_annotated``, ``done`` or ``skipped``
        task: name of annotation task. See also: :class:`remo.task`
        tags: list of tags
    """

    def __init__(
        self, img_filename: str = None, status: str = None, task: str = None, tags: List[str] = None
    ):
        self.img_filename = img_filename
        self.status = status
        self.task = task
        self.tags = tags if tags else []
        self.items = []

    def __str__(self):
        return 'Annotation for image: {}, n_items: {}'.format(self.img_filename, len(self.items))

    def __repr__(self):
        return self.__str__()

    def add_item(self, classes: List[str] = None, bbox: List[int] = None, segment: List[int] = None):
        """
        Adds new annotation item

        Args:
            classes: list of classes
            bbox: list of bbox coordinates like ``['xmin', 'ymin', 'xmax', 'ymax']``
            segment: list of segment coordinates ``[x0, y0, x1, y1, ..., xN, yN]``
        """
        if classes or bbox or segment:
            self.items.append(Annotation.Item(classes, bbox, segment))

    class Item:
        """
        Represents annotation item

        Args:
            classes: list of classes
            bbox: list of bbox coordinates like ``['xmin', 'ymin', 'xmax', 'ymax']``
            segment: list of segment coordinates ``[x0, y0, x1, y1, ..., xN, yN]``
        """

        def __init__(self, classes: List[str] = None, bbox: List[int] = None, segment: List[int] = None):
            self.classes = classes if classes else []
            self.segments = []
            self.bbox = None

            if bbox:
                self.bbox = Annotation.Bbox(*bbox)

            if segment:
                self.segments.append(Annotation.Segment(segment))

        def add_segment(self, points: List[int]):
            """
            Adds new segment. Uses in instance segmentation.

            Args:
                points: list of segment coordinates ``[x0, y0, x1, y1, ..., xN, yN]``
            """
            if points:
                self.segments.append(Annotation.Segment(points))

    class Bbox:
        """
        Represent coordinates of bounding box. Uses in object detection.

        Args:
            xmin: X min
            ymin: Y min
            xmax: X max
            ymax: Y max
        """

        def __init__(self, xmin: int, ymin: int, xmax: int, ymax: int):
            self.xmin = xmin
            self.ymin = ymin
            self.xmax = xmax
            self.ymax = ymax

    class Segment:
        """
        Represents coordinates of segment. Uses in instance segmentation.

        Args:
            points: list of segment coordinates ``[x0, y0, x1, y1, ..., xN, yN]``
        """

        def __init__(self, points: List[int]):
            self.points = [{'x': x, 'y': y} for x, y in zip(points[::2], points[1::2])]
