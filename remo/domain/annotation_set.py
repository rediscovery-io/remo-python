class AnnotationSet:

    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')

    def export_annotations(self, annotation_format=None):
        """
        :param annotation_format: choose format from this list ['json', 'coco']
        :return: annotations
        """
        args = [self.id]
        if annotation_format:
            args.append(annotation_format)
        return self.sdk.export_annotations(*args)
