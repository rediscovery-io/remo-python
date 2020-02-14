class Annotation:
    class Bbox:
        __slots__ = ['xmin', 'ymin', 'xmax', 'ymax']

        def __init__(self, xmin, ymin, xmax, ymax):
            self.xmin = xmin
            self.ymin = ymin
            self.xmax = xmax
            self.ymax = ymax

    class Segment:
        __slots__ = ['points']

        def __init__(self, segment):
            """
            Args:
                segment: list of segment coordinates [x0, y0, x1, y1, ..., xN, yN]
            """
            self.points = [
                {'x': x, 'y': y}
                for x, y in zip(segment[::2], segment[1::2])
            ]

    class Item:
        __slots__ = ['classes', 'segments', 'bbox']

        def __init__(self, classes=None, bbox=None, segment=None):
            """
            Args:
                classes: list of classes
                bbox: list of bbox coordinates like ['xmin', 'ymin', 'xmax', 'ymax']
                segment: list of segment coordinates [x0, y0, x1, y1, ..., xN, yN]
            """
            self.classes = classes if classes else []
            self.segments = []
            self.bbox = None

            if bbox:
                self.bbox = Annotation.Bbox(*bbox)

            if segment:
                self.segments.append(Annotation.Segment(segment))

        def add_segment(self, segment):
            if segment:
                self.segments.append(Annotation.Segment(segment))

    __slots__ = ['file_name', 'status', 'task', 'tags', 'items']

    def __init__(self, file_name=None, status=None, task=None, tags=None):
        """
        Args:
            status: can be "not_annotated", "done" and "skipped"
        """
        self.file_name = file_name
        self.status = status
        self.task = task
        self.tags = tags if tags else []
        self.items = []

    def add_item(self, classes=None, bbox=None, segment=None):
        """
        Args:
            classes: list of classes
            bbox: list of bbox coordinates like ['xmin', 'ymin', 'xmax', 'ymax']
            segment: list of segment coordinates [x0, y0, x1, y1, ..., xN, yN]

        """
        if classes or bbox or segment:
            self.items.append(Annotation.Item(classes, bbox, segment))
