from typing import List, TypeVar

from .annotation import Annotation
from remo.annotation_utils import create_tempfile

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

    def __init__(
        self,
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
        **kwargs
    ):
        from remo import _sdk
        self.sdk = _sdk
        
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

    def add_annotations(self, annotations: List[Annotation]):
        
        """
        Upload of annotations to the annotation set.
        
        Example::
            urls = ['https://remo-scripts.s3-eu-west-1.amazonaws.com/open_images_sample_dataset.zip']
            ds = remo.create_dataset(name = 'D1', urls = urls)
            ann_set = ds.create_annotation_set(annotation_task = 'Object Detection', name = 'test_set')
            
            image_name = '000a1249af2bc5f0.jpg'
            annotations = []

            annotation = remo.Annotation()
            annotation.img_filename = image_name
            annotation.classes='Human hand'
            annotation.bbox=[227, 284, 678, 674]
            annotations.append(annotation)

            annotation = remo.Annotation()
            annotation.img_filename = image_name
            annotation.classes='Fashion accessory'
            annotation.bbox=[496, 322, 544,370]
            annotations.append(annotation)

            ann_set.add_annotations(annotations)
            
        Args:
            annotations: list of Annotation objects
            
        """
            
        temp_path, list_of_classes = create_tempfile(annotations)
        
            
        self.sdk.add_data_to_dataset(
            dataset_id = self.dataset_id,
            paths_to_upload=[temp_path],
            annotation_task=self.task,
            annotation_set_id=self.id
        )

    
    
    
    def add_image_annotation(self, image_id: int, annotation: Annotation):
        """
        Adds new annotation to the image

        Args:
            image_id: image id
            annotation: annotation data
        """
        self.sdk.add_annotation(self.id, image_id, annotation)

    def export_annotations(
        self, annotation_format: str = 'json', export_coordinates: str = 'pixel', full_path: bool = True, export_tags: bool = True
    ):
        """
        Exports annotations in a given format

        Args:
            annotation_format: choose format from this list ['json', 'coco', 'csv']
            full_path: uses full image path (e.g. local path),  it can be one of [True, False], default=True
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            export_tags: exports the tags to a CSV file, it can be one of [True, False], default=True
        Returns:
            annotation file content
        """
        return self.sdk.export_annotations(
            self.id,
            annotation_format=annotation_format,
            export_coordinates=export_coordinates,
            full_path=full_path,
            export_tags=export_tags
        )

    def export_annotations_to_file(
        self,
        output_file: str,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: bool = True,
        export_tags: bool = True
    ):
        """
        Exports annotations in given format and save to output file

        Args:
            output_file: output file to save
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            full_path: uses full image path (e.g. local path),  it can be one of [True, False], default=True
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            export_tags: exports the tags to a CSV file, it can be one of [True, False], default=True
        """
        self.sdk.export_annotations_to_file(
            output_file,
            self.id,
            annotation_format=annotation_format,
            full_path=full_path,
            export_coordinates=export_coordinates,
            export_tags=export_tags
        )

    def classes(self) -> List[str]:
        """
        List classes within the annotation set

        Returns:
            List of classes
        """
        return self.sdk.list_annotation_set_classes(self.id)

    def view(self):
        """
        Opens browser on the annotation tool page for this annotation set
        """
        return self.sdk.view_annotation_tool(self.id)

    def view_stats(self):
        """
        Opens browser on annotation set insights page
        """
        return self.sdk.view_annotation_stats(self.id)
