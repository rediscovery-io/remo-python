from typing import List, TypeVar

Dataset = TypeVar('Dataset')


class AnnotationSet:
    """
    Remo annotation set

    Args:
        id: annotation set id
        name: annotation set name
        task: annotation task. See also: :class:`remo.task`
        dataset_id: dataset id
        total_classes: total annotation classes
        updated_at: date, when annotation set was last updated
        released_at: annotation set release date
        total_images: total number of images
        top3_classes: top 3 classes in annotation set
        total_annotation_objects: total number of annotation objects in annotation set
    """

    __slots__ = (
        'sdk',
        'id',
        'name',
        'task',
        'dataset_id',
        'total_classes',
        'updated_at',
        'released_at',
        'total_images',
        'top3_classes',
        'total_annotation_objects',
    )

    def __init__(
            self,
            sdk,
            id: int = None,
            name: str = None,
            task: str = None,
            dataset_id: int = None,
            total_classes=None,
            updated_at=None,
            released_at=None,
            total_images: int = None,
            top3_classes=None,
            total_annotation_objects: int = None,
    ):
        self.sdk = sdk
        self.id = id
        self.name = name
        self.task = task
        self.dataset_id = dataset_id
        self.total_classes = total_classes
        self.updated_at = updated_at
        self.released_at = released_at
        self.total_images = total_images
        self.top3_classes = top3_classes
        self.total_annotation_objects = total_annotation_objects

    def __str__(self):
        return "Annotation set {id} - '{name}', task: {task}, #classes: {total_classes}".format(
            id=self.id, name=self.name, task=self.task, total_classes=self.total_classes
        )

    def __repr__(self):
        return self.__str__()

    def export_annotations(
            self, annotation_format: str = 'json', export_coordinates: str = 'pixel', full_path: str = 'true'
    ):
        """
        Exports annotations in a given format

        Args:
            annotation_format: choose format from this list ['json', 'coco', 'csv']
            full_path: uses full image path (e.g. local path), can be one of ['true', 'false'], default='false'
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'

        Returns:
            annotation file content
        """
        return self.sdk.export_annotations(
            self.id,
            annotation_format=annotation_format,
            export_coordinates=export_coordinates,
            full_path=full_path,
        )

    def export_annotation_to_csv(self, output_file: str, dataset: Dataset):
        """
        .. deprecated:: 0.0.13
            Use `:func:export_annotations` instead

        Exports annotations to a .csv file
        Args:
            output_file: .csv path
            dataset: dataset to export annotations from
        """
        self.sdk.export_annotation_to_csv(self.id, output_file, dataset)

    def get_classes(self) -> List[str]:
        """
        List classes within the annotation set

        Returns:
            List of classes
        """
        return self.sdk.list_annotation_classes(self.id)

    def view(self):
        """
        Opens browser on the annotation tool page for this annotation set
        """
        self.sdk.view_annotation_tool(self.id)

    def view_insights(self):
        """
        Opens browser on annotation set insights page
        """
        self.sdk.view_annotation_insights(self.id)
