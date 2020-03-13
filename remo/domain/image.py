import os
import shutil
from typing import TypeVar, List


Annotation = TypeVar('Annotation')
AnnotationSet = TypeVar('AnnotationSet')


class Image:
    """
    Remo image

    Args:
        id: image id
        name: image file name
        dataset_id: dataset id
        path: local path, if available
        url: image remo internal URL
        size: file size in bytes
        width: image width in pixels
        height: image height in pixels
        upload_date: upload date
    """

    def __init__(
        self,
        id: int = None,
        name: str = None,
        dataset_id: int = None,
        path: str = None,
        url: str = None,
        size: int = None,
        width: int = None,
        height: int = None,
        upload_date: str = None,
        **kwargs
    ):
        from remo import _sdk

        self.sdk = _sdk

        self.id = id
        self.name = name
        self.dataset_id = dataset_id
        self.path = path
        self.url = url
        self.size = size
        self.width = width
        self.height = height
        self.upload_date = upload_date

    def __str__(self):
        return 'Image: {} - {}'.format(self.id, self.name)

    def __repr__(self):
        return self.__str__()

    def get_content(self) -> bytes:
        """
        Retrieves image file content

        Returns:
            image binary data
        """
        if not self.url:
            print('ERROR: image url is not set')
            return

        return self.sdk.get_image_content(self.url)

    def save_to(self, dir_path: str):
        """
        Save image to giving directory

        Args:
            dir_path: path to the directory
        """
        dir_path = self.sdk._resolve_path(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, self.name)

        if self.path:
            shutil.copy(self.path, file_path)
            return

        img_content = self.get_content()
        if not img_content:
            return

        self.sdk._save_to_file(img_content, file_path)

    def list_annotation_sets(self) -> List[AnnotationSet]:
        """
        Lists annotations sets

        Returns:
            List[:class:`remo.AnnotationSet`]
        """
        return self.sdk.list_annotation_sets(self.dataset_id)

    def annotations(self, annotation_set_id: int) -> List[Annotation]:
        """
        Retrieves image annotations from giving annotation set

        Args:
            annotation_set_id: annotation set id

        Returns:
             List[:class:`remo.Annotation`]
        """
        return self.sdk.list_image_annotations(self.dataset_id, annotation_set_id, self.id)

    def get_annotation_set(self, annotation_set_id: int = None) -> AnnotationSet:

        ds = self.sdk.get_dataset(self.dataset_id)
        return ds.get_annotation_set(annotation_set_id)

    def add_annotation(self, annotation: Annotation, annotation_set_id: int = None):
        """
        Adds new annotation to the image

        Args:
            annotation_set_id: annotation set id
            annotation: annotation data
        """
        if not annotation_set_id:
            annotation_set = self.get_annotation_set()
            annotation_set_id = annotation_set.id

        if annotation_set_id:
            self.sdk.add_annotations_to_image(annotation_set_id, self.id, annotation)
        else:
            print('ERROR: annotation set not defined')

    def view(self):
        """
        Opens browser on image view for the image
        """
        return self.sdk.view_image(self.id, self.dataset_id)

    def view_annotate(self, annotation_set_id: int):
        """
        Opens browser on the annotation tool for giving annotation set

        Args:
            annotation_set_id: annotation set id
        """
        return self.sdk.view_annotate_image(annotation_set_id, self.id)
