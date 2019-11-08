class AnnotationSet:

    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.task = kwargs.get('task')
        self.total_classes = kwargs.get('total_classes')
        self.released_at = kwargs.get('released_at')
        self.updated_at = kwargs.get('updated_at')
        self.total_images = kwargs.get('total_images')
        self.top3_classes = kwargs.get('top3_classes')

    def __str__(self):
        return "Annotation set {id} - '{name}', task: {task}, #classes: {total_classes}".format(
            id=self.id, name=self.name, task=self.task, total_classes=self.total_classes)

    def __repr__(self):
        return self.__str__()

    def get_annotations(self, annotation_format=None):
        """
        :param annotation_format: choose format from this list ['json', 'coco']
        :return: annotations
        """
        args = [self.id]
        if annotation_format:
            args.append(annotation_format)
        return self.sdk.export_annotations(*args)
