from operator import itemgetter 

class AnnotationSet:

    def __init__(self, sdk, **kwargs):
        self.sdk = sdk
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.task = kwargs.get('task')
        self.dataset_id = kwargs.get('dataset_id')
        self.total_classes = kwargs.get('total_classes')
        self.updated_at = kwargs.get('updated_at')
        self.released_at = kwargs.get('released_at')
        self.total_images = kwargs.get('total_images')
        self.top3_classes = kwargs.get('top3_classes')
        self.total_annotation_objects = kwargs.get('total_annotation_objects')
        
    def __str__(self):
        return "Annotation set {id} - '{name}', task: {task}, #classes: {total_classes}".format(
            id=self.id, name=self.name, task=self.task, total_classes=self.total_classes)

    def __repr__(self):
        return self.__str__()

    def get_annotations(self, annotation_format='json'):
        """
        :param annotation_format: choose format from this list ['json', 'coco']
        :return: annotations
        """
        return self.sdk.get_annotations(self.id, annotation_format)

    def export_annotation_to_csv(self, output_file, dataset):
        """
        Takes annotations and saves as a .csv file
        Args:
            output_file: .csv path
        """
        self.sdk._export_annotation_to_csv(self.id, output_file, dataset)
        
    def get_classes(self):
        """
        Returns list of dictionaries containing information of the classes within the annotation set
        """
        res = self.sdk._list_annotation_classes(self.id)
        results = res.get('results')
        class_list = list(map(itemgetter('class'), results))
        return class_list
        
    def view(self):
        self.sdk.view_annotation_set(self.id)

    def view_stats(self):
        self.sdk.view_annotation_stats(self.id)
