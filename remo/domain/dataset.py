import os
from typing import List, TypeVar

from .annotation import Annotation
from .image import Image
from remo.annotation_utils import create_tempfile

AnnotationSet = TypeVar('AnnotationSet')


class Dataset:
    """
    Remo dataset

    Args:
        id: dataset id
        name: dataset name
        quantity: number of images
    """

    def __init__(self, id: int = None, name: str = None, quantity: int = 0, **kwargs):
        from remo import _sdk

        self.sdk = _sdk
        self.id = id
        self.name = name
        self.n_images = quantity

    def __str__(self):
        return "Dataset {id:2d} - {name:5s} - {n_images:,} images".format(
            id=self.id, name="'{}'".format(self.name), n_images=self.n_images
        )

    def __repr__(self):
        return self.__str__()

    def info(self):
        """
        Prints basic info about the dataset:
        
        - Dataset name
        - Dataset ID
        - Number of images contained in the dataset
        - Number of annotation sets contained in the dataset

        """
        info = """Dataset name: {name}
Dataset ID: {id}
Images: {n_images}
Annotation Sets: {n_annotation_sets}""".format(
            id=self.id, name=self.name, n_images=self.n_images, n_annotation_sets=len(self.annotation_sets())
        )
        print(info)

    def add_data(
        self,
        local_files: List[str] = None,
        paths_to_upload: List[str] = None,
        urls: List[str] = None,
        annotation_task: str = None,
        folder_id: int = None,
        annotation_set_id: int = None,
        class_encoding=None,
        wait_for_complete=True,
    ) -> dict:
        """
        Adds images and/or annotations to the dataset.

        Use the parameters as follows:

        - Use ``local files`` to link (rather than copy) images.
        - Use ``paths_to_upload`` if you want to copy image files or archive files.
        - Use ``urls`` to download from the web images, annotations or archives.

        In terms of supported formats:

        - Adding images: support for ``jpg``, ``jpeg``, ``png``, ``tif``
        - Adding annotations: to add annotations, you need to specify the annotation task and make sure the specific file format is one of those supported. See documentation here: https://remo.ai/docs/annotation-formats/
        - Adding archive files: support for ``zip``, ``tar``, ``gzip``

        Example::
            urls = ['https://remo-scripts.s3-eu-west-1.amazonaws.com/open_images_sample_dataset.zip']
            my_dataset = remo.create_dataset(name = 'D1', urls = urls)
            my_dataset.add_data(local_files=annotation_files, annotation_task = 'Object detection')

        Args:
            dataset_id: id of the dataset to add data to

            local_files: list of files or directories containing annotations and image files
                Remo will create smaller copies of your images for quick previews but it will point at the original files to show original resolutions images.
                Folders will be recursively scanned for image files.


            paths_to_upload: list of files or directories containing images, annotations and archives.
                These files will be copied inside .remo folder.
                Folders will be recursively scanned for image files.
                Unpacked archive will be scanned for images, annotations and nested archives.

            urls: list of urls pointing to downloadable target, which can be image, annotation file or archive.

            annotation_task: annotation tasks tell remo how to parse annotations. See also: :class:`remo.task`.

            folder_id: specifies target virtual folder in the remo dataset. If None, it adds to the root level.

            annotation_set_id: specifies target annotation set in the dataset. If None, it adds to the default annotation set.

            class_encoding: specifies how to convert labels in annotation files to readable labels. If None,  Remo will try to interpret the encoding automatically - which for standard words, means they will be read as they are.
                See also: :class:`remo.class_encodings`.

            wait_for_complete: if True, the function waits for upload data to complete

        Returns:
            Dictionary with results for linking files, upload files and upload urls::

                {
                    'files_link_result': ...,
                    'files_upload_result': ...,
                    'urls_upload_result': ...
                }


        """

        if annotation_set_id:
            annotation_set = self.get_annotation_set(annotation_set_id)
            if not annotation_set:
                raise Exception('Annotation set ID = {} not found'.format(annotation_set_id))

        return self.sdk.add_data_to_dataset(
            self.id,
            local_files=local_files,
            paths_to_upload=paths_to_upload,
            urls=urls,
            annotation_task=annotation_task,
            folder_id=folder_id,
            annotation_set_id=annotation_set_id,
            class_encoding=class_encoding,
            wait_for_complete=wait_for_complete,
        )

    def fetch(self):
        """
        Updates dataset information from server
        """
        dataset = self.sdk.get_dataset(self.id)
        self.__dict__.update(dataset.__dict__)

    def annotation_sets(self) -> List[AnnotationSet]:
        """
        Lists the annotation sets within the dataset.

        Returns:
            List[:class:`remo.AnnotationSet`]
        """
        return self.sdk.list_annotation_sets(self.id)

    def add_annotations(
        self,
        annotations: List[Annotation],
        annotation_set_id: int = None,
        create_new_annotation_set: bool = False,
    ):
        """
        Fast upload of annotations to the Dataset.

        If annotation_set_id is not provided, annotations will be added to:

            - the only annotation set present, if the Dataset has exactly one Annotation Set and the tasks match
            - a new annotation set, if the Dataset doesn't have any Annotation Sets or if ceate_new_annotation_set = True

        Otherwise, annotations will be added to the Annotation Set specified by annotation_set_id.

        Example::
            urls = ['https://remo-scripts.s3-eu-west-1.amazonaws.com/open_images_sample_dataset.zip']
            my_dataset = remo.create_dataset(name = 'D1', urls = urls)
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

            my_dataset.add_annotations(annotations)

        Args:
            annotations: list of Annotation objects
            (optional) annotation_set_id: annotation set id
            (optional) create_new_annotation_set: if True, a new annotation set will be created


        """
        if annotation_set_id and create_new_annotation_set:
            raise Exception(
                "You passed an annotation set but also set create_new_annotation_set = True. You can't have both."
            )

        if annotation_set_id:
            annotation_set = self.get_annotation_set(annotation_set_id)
        else:
            annotation_sets = self.annotation_sets()
            if len(annotation_sets) > 0:
                annotation_set = self.get_annotation_set()
                annotation_set_id = annotation_set.id

        temp_path, list_of_classes = create_tempfile(annotations)

        if create_new_annotation_set or (not annotation_set_id):
            n_annotation_sets = len(self.annotation_sets())
            self.create_annotation_set(
                annotation_task=annotations[0].task,
                name='my_ann_set_{}'.format(n_annotation_sets + 1),
                classes=list_of_classes,
                path_to_annotation_file=temp_path,
            )

        else:
            self.add_data(
                annotation_task=annotation_set.task,
                annotation_set_id=annotation_set.id,
                paths_to_upload=[temp_path],
            )

        # TODO ALR: removing the temp_path doesn't work on Windows, hence the try except as a temp fix

        try:
            os.remove(temp_path)
        except:
            pass

    def export_annotations(
        self,
        annotation_set_id: int = None,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: bool = True,
        export_tags: bool = True
    ) -> bytes:
        """
        Export annotations for a given annotation set

        Args:
            annotation_set_id: annotation set id, by default will be used default_annotation_set
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            full_path: uses full image path (e.g. local path),  it can be one of [True, False], default=True
            export_tags: exports the tags to a CSV file, it can be one of [True, False], default=True
            
        Returns:
            annotation file content
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        if annotation_set:
            return annotation_set.export_annotations(
                annotation_format=annotation_format,
                export_coordinates=export_coordinates,
                full_path=full_path,
                export_tags=export_tags
            )

        print('ERROR: annotation set not defined')

    def export_annotations_to_file(
        self,
        output_file: str,
        annotation_set_id: int = None,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: bool = True,
        export_tags: bool = True
    ):
        """
        Exports annotations in given format and save to output file

        Args:
            output_file: output file to save
            annotation_set_id: annotation set id
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            full_path: uses full image path (e.g. local path),  it can be one of [True, False], default=True
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            export_tags: exports the tags to a CSV file, it can be one of [True, False], default=True
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        if annotation_set:
            self.sdk.export_annotations_to_file(
                output_file,
                annotation_set.id,
                annotation_format=annotation_format,
                full_path=full_path,
                export_coordinates=export_coordinates,
                export_tags=export_tags
            )
        else:
            print('ERROR: annotation set not defined')

    def list_image_annotations(self, annotation_set_id: int, image_id: int) -> List[Annotation]:
        """
        Retrieves annotations for a given image

        Args:
            annotation_set_id: annotation set id
            image_id: image id

        Returns:
            List[:class:`remo.Annotation`]
        """
        return self.sdk.list_image_annotations(self.id, annotation_set_id, image_id)

    def create_annotation_set(
        self, annotation_task: str, name: str, classes: List[str] = [], path_to_annotation_file: str = None
    ) -> AnnotationSet:
        """
        Creates a new annotation set within the dataset
        If path_to_annotation_file is provided, it populates it with the given annotations.
        The first created annotation set for the given dataset, is considered the default one.

        Args:
            annotation_task: annotation task. See also: :class:`remo.task`
            name: annotation set name
            classes: list of classes to prepopulate the annotation set. Example: ['Cat', 'Dog']. Default is no classes
            path_to_annotation_file: path to .csv annotation file

        Returns:
            :class:`remo.AnnotationSet`
        """
        annotation_set = self.sdk.create_annotation_set(annotation_task, self.id, name, classes)

        if annotation_set and path_to_annotation_file:
            self.add_data(
                paths_to_upload=[path_to_annotation_file],
                annotation_task=annotation_task,
                annotation_set_id=annotation_set.id,
            )

            annotation_set = self.sdk.get_annotation_set(annotation_set.id)

        return annotation_set

    def get_annotation_set(self, annotation_set_id: int = None) -> AnnotationSet:
        """
        Retrieves annotation set with given id.
        If no annotation set id is passed, it returns the default annotation set.

        Args:
            annotation_set_id: annotation set id

        Returns:
             :class:`remo.AnnotationSet`
        """
        if not annotation_set_id:
            return self.default_annotation_set()

        annotation_set = self.sdk.get_annotation_set(annotation_set_id)
        if annotation_set and annotation_set.dataset_id == self.id:
            return annotation_set
        else:
            raise Exception(
                'Annotation set with ID = {} is not part of dataset {}. You can check the list of annotation sets in your dataset using dataset.annotation_sets()'.format(
                    annotation_set_id, self.__str__()
                )
            )

    def default_annotation_set(self) -> AnnotationSet:
        """
        If the dataset has only one annotation set, it returns that annotation set.
        Otherwise, it raises an exception.
        """
        annotation_sets = self.annotation_sets()

        if len(annotation_sets) > 1:
            raise Exception(
                'Define which annotation set you want to use. '
                + self.__str__()
                + ' has '
                + str(len(annotation_sets))
                + ' annotation sets. You can see them with `my_dataset.annotation_sets()`'
            )

        elif len(annotation_sets) == 0:
            raise Exception(
                self.__str__()
                + " doesn't have any annotations. You can check the list of annotation sets with `my_dataset.annotation_sets()`"
            )

        return annotation_sets[0]

    def get_annotation_statistics(self, annotation_set_id: int = None):
        """
        Prints annotation statistics of all the available annotation sets within the dataset

        Returns:
            list of dictionaries with fields annotation set id, name, num of images, num of classes, num of objects, top3 classes, release and update dates
        """

        # TODO: ALR - Improve output formatting
        # TODO: ALR - Optional annotation set id as input
        statistics = []
        for ann_set in self.annotation_sets():

            if (annotation_set_id is None) or (annotation_set_id == ann_set.id):
                stat = {
                    'AnnotationSet ID': ann_set.id,
                    'AnnotationSet name': ann_set.name,
                    'n_images': ann_set.total_images,
                    'n_classes': ann_set.total_classes,
                    'n_objects': ann_set.total_annotation_objects,
                    'top_3_classes': ann_set.top3_classes,
                    'creation_date': ann_set.released_at,
                    'last_modified_date': ann_set.updated_at,
                }

                statistics.append(stat)
        return statistics

    def classes(self, annotation_set_id: int = None) -> List[str]:
        """
        Lists all the classes within the dataset

        Args:
             annotation_set_id: annotation set id. If not specified the default annotation set is considered.

        Returns:
            List of classes
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        if annotation_set:
            return annotation_set.classes()

    def annotations(self, annotation_set_id: int = None) -> List[Annotation]:
        """
        Returns all annotations for a given annotation set.
        If no annotation set is specified, the default annotation set will be used

        Args:
            annotation_set_id: annotation set id

        Returns:
             List[:class:`remo.Annotation`]
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        if annotation_set:
            return self.sdk.list_annotations(self.id, annotation_set.id)
        print('ERROR: annotation set was not defined.')

    def images(self, limit: int = None, offset: int = None) -> List[Image]:
        """
        Lists images within the dataset

        Args:
            limit: the number of images to be listed
            offset: specifies offset

        Returns:
            List[:class:`remo.Image`]

        Example::
            my_dataset.images()

        """
        return self.sdk.list_dataset_images(self.id, limit=limit, offset=offset)

    def image(self, img_filename=None, img_id=None) -> Image:
        """
        Returns the :class:`remo.Image` with matching img_filename or img_id.
        Pass either img_filename or img_id.

        Args:
            img_filename: filename of the Image to retrieve
            img_id: id of the the Image to retrieve

        Returns:
            :class:`remo.Image`
        """
        # TODO ALR: do we need to raise an error if no image is found?
        # TODO ALR: we have a sdk.get_image by img_id. Should we implement get_image by img_name in the server for faster processing?

        if (img_filename) and (img_id):
            raise Exception("You passed both img_filename and img_id. Pass only one of the two")

        if img_filename:
            list_of_images = self.images()
            for i_image in list_of_images:
                if i_image.name == img_filename:
                    return i_image
        elif img_id:
            return self.sdk.get_image(img_id)

    def delete(self):
        """
        Deletes dataset
        """
        self.sdk.delete_dataset(self.id)

    def search(self, classes=None, task: str = None):
        """
        Given a list of classes and annotation task, it returns a list of all the images with mathcing annotations

        Args:
            classes: string or list of strings - search for images which match all given classes
            task: annotation task. See also: :class:`remo.task`

        Returns:
            subset of the dataset
        """
        # TODO: add implementation
        return self.sdk.search_images(classes, task, self.id)

    def view(self):
        """
        Opens browser on dataset page
        """
        # print('self.sdk', self.sdk, type(self.sdk))
        return self.sdk.view_dataset(self.id)

    def view_annotate(self, annotation_set_id: int = None):
        """
        Opens browser on the annotation tool for the given annotation set

        Args:
              annotation_set_id: annotation set id. If not specified, default one be used.
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        if annotation_set:
            return annotation_set.view()
        else:
            print('ERROR: annotation set was not defined.')

    def view_annotation_stats(self, annotation_set_id: int = None):
        """
        Opens browser on annotation set insights page

        Args:
            annotation_set_id: annotation set id. If not specified, default one be used.
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        if annotation_set:
            return annotation_set.view_stats()
        else:
            print('ERROR: annotation set was not defined.')

    def view_image(self, image_id: int):
        """
        Opens browser on image view page for the given image

        Args:
            image_id: image id
        """
        return self.sdk.view_image(image_id, self.id)
