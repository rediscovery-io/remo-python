import os
import time
from typing import List
import csv
from .domain import Image, Dataset, AnnotationSet, class_encodings, Annotation
from .api import API

from .endpoints import frontend
from .viewer import factory


class SDK:
    """
    Creates sdk object, and checks connection to server

    Args:
        server: server host name, e.g. ``http://localhost:8123/``
        email: user credentials
        password: user credentials
        viewer: allows to choose between browser, electron and jupyter viewer.
            To be able change viewer, you can use :func:`set_viewer` function. See example.

    Example::

        import remo

        remo.set_viewer('browser')

    """

    def __init__(self, server: str, email: str, password: str, viewer: str = 'browser'):
        self.api = API(server, email, password)

        self.viewer = None
        self.set_viewer(viewer)

    def set_public_url(self, public_url: str):
        self.api.set_public_url(public_url)

    def set_viewer(self, viewer: str):
        """
        Allows to choose one of available viewers

        Args:
            viewer: choose between 'browser', 'electron' and 'jupyter' viewer
        """
        self.viewer = factory(viewer)

    def create_dataset(
        self,
        name: str,
        local_files: List[str] = None,
        paths_to_upload: List[str] = None,
        urls: List[str] = None,
        annotation_task: str = None,
        class_encoding=None,
        wait_for_complete=True
    ) -> Dataset:
        """
        Creates a new dataset in Remo and optionally populate it with images and annotations.
        To add annotations, you need to specify an annotation task.

        Args:
            name: name of the dataset.

            local_files: list of files or directories.
                These files will be linked.
                Folders will be recursively scanned for image files: ``jpg``, ``png``, ``tif``.

            paths_to_upload: list of files or directories.
                These files will be copied. Supported files: images, annotations and archives.

                - image files: ``jpg``, ``png``, ``tif``.
                - annotation files: ``json``, ``xml``, ``csv``.
                - archive files: ``zip``, ``tar``, ``gzip``.
                    Unpacked archive will be scanned for images, annotations and nested archives.

            urls: list of urls pointing to downloadable target, which can be image, annotation file or archive.

            annotation_task: specifies annotation task. See also: :class:`remo.task`.

            class_encoding: specifies how to convert class labels in annotation files to classes.
                See also: :class:`remo.class_encodings`.

            wait_for_complete: blocks function until upload data completes

        Returns:
            :class:`remo.Dataset`
        """

        json_data = self.api.create_dataset(name)
        ds = Dataset(**json_data)
        ds.add_data(
            local_files, paths_to_upload, urls, annotation_task=annotation_task, class_encoding=class_encoding,
            wait_for_complete=wait_for_complete
        )
        ds.fetch()
        return ds

    def add_data_to_dataset(
        self,
        dataset_id: int,
        local_files: List[str] = None,
        paths_to_upload: List[str] = None,
        urls: List[str] = None,
        annotation_task: str = None,
        folder_id: int = None,
        annotation_set_id: int = None,
        class_encoding=None,
        wait_for_complete=True
    ) -> dict:
        """
        Adds images and/or annotations to an existing dataset.
        Use ``local files`` to link (rather than copy) images. Use ``paths_to_upload`` if you want to copy image files or archive files. Use ``urls`` to download from the web images, annotations or archives.
        Adding images: support for ``jpg``,``jpeg``, ``png``, ``tif``
        Adding annotations: to add annotations, you need to specify the annotation task and make sure the specific file format is one of those supported. See documentation here: https://remo.ai/docs/annotation-formats/
        Adding archive files: support for ``zip``, ``tar``, ``gzip``
        
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

            annotation_set_id: specifies target annotation set in the dataset. If None: if no annotation set exists, one will be automatically created. If exactly one annotation set already exists, it will add annotations to that annotation set, provided the task matches.
            
            class_encoding: specifies how to convert labels in annotation files to readable labels. If None,  Remo will try to interpret the encoding automatically - which for standard words, means they will be read as they are. 
                See also: :class:`remo.class_encodings`.

            wait_for_complete: blocks function until upload data completes

        Returns:
            Dictionary with results for linking files, upload files and upload urls::

                {
                    'files_link_result': ...,
                    'files_upload_result': ...,
                    'urls_upload_result': ...
                }

        """
        kwargs = {
            'annotation_task': annotation_task,
            'folder_id': folder_id,
            'annotation_set_id': annotation_set_id,
        }

        # logic to deal with the case where we are trying to upload annotations without specifying the annotation set id
        if annotation_task and (not annotation_set_id):
            annotation_sets = self.list_annotation_sets(dataset_id)

            if len(annotation_sets) > 1:
                raise Exception(
                    'Define which annotation set you want to use. Dataset {} has {} annotation sets. '
                    'You can see them with my_dataset.annotation_sets()'.format(dataset_id, len(annotation_sets))
                )

            elif len(annotation_sets) == 1:
                kwargs['annotation_set_id'] = annotation_sets[0].id

        # check values
        if local_files:
            self._raise_value_error(local_files, 'local_files', list, 'list of paths')
        if paths_to_upload:
            self._raise_value_error(paths_to_upload, 'paths_to_upload', list, 'list of paths')
        if urls:
            self._raise_value_error(urls, 'urls', list, 'list of URLs')

        session_id = self.api.create_new_upload_session(dataset_id)
        kwargs['session_id'] = session_id

        if local_files:
            encoding = class_encodings.for_linking(class_encoding)
            self.api.upload_local_files(
                dataset_id, local_files, class_encoding=encoding, **kwargs
            )

        if paths_to_upload:
            encoding = class_encodings.for_upload(class_encoding)
            self.api.bulk_upload_files(
                dataset_id, paths_to_upload, class_encoding=encoding, **kwargs
            )

        if urls:
            encoding = class_encodings.for_linking(class_encoding)
            self.api.upload_urls(
                dataset_id, urls, class_encoding=encoding, **kwargs
            )

        self.api.complete_upload_session(session_id)

        if not wait_for_complete:
            return {'session_id': session_id}

        return self._report_processing_data_progress(session_id)

    def _report_processing_data_progress(self, session_id: str):
        """
        Reports progress for upload session

        Args:
            session_id: upload session id

        Returns:
             session status
        """
        def format_msg(msg, *args, max_length=100):
            msg = msg.format(*args)
            return '{} {}'.format(msg, ' ' * (max_length - len(msg)))

        def print_session_errors(data, key='error'):
            for err in data:
                msg = err[key] if 'value' not in err else '{}: {}'.format(err['value'], err[key])
                print(msg)

        def print_session_warnings(data):
            print_session_errors(data, key='warning')

        def print_file_errors(data, key='errors'):
            errors = data.get(key, [])
            for err in errors:
                filename, errs = err['filename'], err[key]
                msg = errs[0] if len(errs) == 1 else '\n * ' + '\n * '.join(errs)
                msg = '{}: {}'.format(filename, msg)
                print(msg)

        def print_file_warnings(data):
            print_file_errors(data, key='warnings')

        last_msg = ''
        while True:
            session = self.api.get_upload_session_status(session_id)
            if not session:
                raise Exception('Something went wrong, got empty session from server')

            status = session.get('status')
            substatus = session.get('substatus')
            uploaded = session['uploaded']['total']

            if status == 'not complete':
                msg = format_msg('Acquiring data - {} files, {}', uploaded['items'], uploaded['human_size'])
                if msg != last_msg:
                    print(msg, end='\r')
                    last_msg = msg

            elif status == 'pending':
                msg = format_msg('Acquiring data - completed')
                if msg != last_msg:
                    print(msg)
                    last_msg = msg

            elif status == 'in progress':
                msg = 'Processing data'
                if substatus:
                    msg = '\r{}'.format(substatus)
                else:
                    msg = '{}'.format(msg)
                msg = format_msg(msg)
                if msg != last_msg:
                    print(msg, end=' ')
                    last_msg = msg

            elif status in ('done', 'failed'):
                print(format_msg('Processing data - completed'))
                msg = 'Data upload completed' if status == 'done' else 'Data upload completed with some errors:'
                print(msg)

                if status == 'failed':
                    print_session_errors(session.get('errors', []))
                    print_file_errors(session['images'])
                    print_file_errors(session['annotations'])

                if session.get('warnings', []) or session['images'].get('warnings', []) or session['annotations'].get('warnings', []):
                    print('With some warnings:')
                    print_session_warnings(session.get('warnings', []))
                    print_file_warnings(session['images'])
                    print_file_warnings(session['annotations'])

                return session
            time.sleep(1)

    @staticmethod
    def _raise_value_error(value, value_name, expected_type, expected_description):
        if not isinstance(value, expected_type):
            raise ValueError(
                'Parameter "{}" should be a {}, but instead is a {}.'.format(
                    value_name, expected_description, type(value)
                )
            )

    def list_datasets(self) -> List[Dataset]:
        """
        Lists the available datasets

        Returns:
            List[:class:`remo.Dataset`]
        """
        json_data = self.api.list_datasets()
        return [Dataset(**ds_item) for ds_item in json_data.get('results', [])]

    def get_dataset(self, dataset_id: int) -> Dataset:
        """
        Retrieves a dataset with given dataset id.

        Args:
            dataset_id: dataset id

        Returns:
            :class:`remo.Dataset`
        """
        json_data = self.api.get_dataset(dataset_id)

        if json_data.get('detail') == "Not found.":
            raise Exception(
                "Dataset ID {} not found. "
                "You can check your existing datasets with `remo.list_datasets()`".format(dataset_id)
            )

        return Dataset(**json_data)

    def delete_dataset(self, dataset_id: int):
        """
        Deletes dataset

        Args:
            dataset_id: dataset id
        """
        self.api.delete_dataset(dataset_id)

    def list_annotation_sets(self, dataset_id: int) -> List[AnnotationSet]:
        """
        Returns a list of AnnotationSet containing all the AnnotationSets of a given dataset

        Args:
            dataset_id: dataset id

        Returns:
            List[:class:`remo.AnnotationSet`]
        """

        result = self.api.list_annotation_sets(dataset_id)
        return [
            AnnotationSet(
                id=annotation_set['id'],
                name=annotation_set['name'],
                updated_at=annotation_set['updated_at'],
                task=annotation_set['task']['name'],
                dataset_id=dataset_id,
                top3_classes=annotation_set['statistics']['top3_classes'],
                total_images=annotation_set['statistics']['annotated_images_count'],
                total_classes=annotation_set['statistics']['total_classes'],
                total_annotation_objects=annotation_set['statistics']['total_annotation_objects'],
            )
            for annotation_set in result.get('results', [])
        ]

    def get_annotation_set(self, annotation_set_id: int) -> AnnotationSet:
        """
        Retrieves annotation set

        Args:
            annotation_set_id: annotation set id

        Returns:
             :class:`remo.AnnotationSet`
        """
        annotation_set = self.api.get_annotation_set(annotation_set_id)

        if 'detail' in annotation_set:
            raise Exception(
                'Annotation set with ID = {} not found. '
                'You can check the list of annotation sets in your dataset using dataset.annotation_sets()'.format(annotation_set_id)
            )

        return AnnotationSet(
            id=annotation_set['id'],
            name=annotation_set['name'],
            updated_at=annotation_set['updated_at'],
            task=annotation_set['task']['name'],
            dataset_id=annotation_set['dataset']['id'],
            total_classes=len(annotation_set['classes']),
        )

    def export_annotations(
        self,
        annotation_set_id: int,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: bool = True,
        export_tags : bool = True
    ) -> bytes:
        """
        Exports annotations in given format

        Args:
            annotation_set_id: annotation set id
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            full_path: uses full image path (e.g. local path),  it can be one of [True, False], default=True
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            export_tags: exports the tags to a CSV file, it can be one of [True, False], default=True
        Returns:
            annotation file content
        """
        return self.api.export_annotations(
            annotation_set_id,
            annotation_format=annotation_format,
            export_coordinates=export_coordinates,
            full_path=full_path,
            export_tags=export_tags
        )

    def export_annotations_to_file(
        self,
        output_file: str,
        annotation_set_id: int,
        annotation_format: str = 'json',
        export_coordinates: str = 'pixel',
        full_path: bool = True,
        export_tags: bool = True
    ):
        """
        Exports annotations in given format

        Args:
            output_file: output file to save
            annotation_set_id: annotation set id
            annotation_format: can be one of ['json', 'coco', 'csv'], default='json'
            full_path: uses full image path (e.g. local path),  it can be one of [True, False], default=True
            export_coordinates: converts output values to percentage or pixels, can be one of ['pixel', 'percent'], default='pixel'
            export_tags: exports the tags to a CSV file, it can be one of [True, False], default=True
        """
        content = self.export_annotations(
            annotation_set_id,
            annotation_format=annotation_format,
            export_coordinates=export_coordinates,
            full_path=full_path,
            export_tags=export_tags
        )
        self._save_to_file(content, output_file)

    def _save_to_file(self, content: bytes, output_file: str):
        output_file = self._resolve_path(output_file)
        dir_path = os.path.dirname(output_file)
        os.makedirs(dir_path, exist_ok=True)
        with open(output_file, 'wb') as out_file:
            out_file.write(content)

    @staticmethod
    def _resolve_path(path: str):
        if path.startswith('~'):
            path = os.path.expanduser(path)
        return os.path.realpath(os.path.abspath(path))

    def get_annotation_info(self, dataset_id: int, annotation_set_id: int, image_id: int) -> list:
        """
        Returns current annotations for the image

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id
            image_id: image id

        Returns:
            annotations info - list of annotation objects or classes
        """
        resp = self.api.get_annotation_info(dataset_id, annotation_set_id, image_id)
        return resp.get('annotation_info', [])

    def list_image_annotations(
        self, dataset_id: int, annotation_set_id: int, image_id: int
    ) -> List[Annotation]:
        """
        Returns annotations for a given image

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id
            image_id: image id

        Returns:
             List[:class:`remo.Annotation`]
        """
        annotation_items = self.get_annotation_info(dataset_id, annotation_set_id, image_id)
        img = self.get_image(image_id)
        if not img:
            return None

        annotations = []
        for item in annotation_items:
            annotation = Annotation(img_filename=img.name)

            if 'lower' in item:
                annotation.classes = item.get('name')
            else:
                classes = [cls.get('name') for cls in item.get('classes', [])]
                annotation.classes = classes

                points = item.get('coordinates')
                if len(points) == 2:
                    bbox = [points[0]['x'], points[0]['y'], points[1]['x'], points[1]['y']]
                    annotation.bbox = bbox

                elif len(points) > 2:
                    segment = []
                    for p in points:
                        segment.append(p['x'])
                        segment.append(p['y'])
                    annotation.segment = segment

            annotations.append(annotation)

        return annotations

    def list_annotations(self, dataset_id: int, annotation_set_id: int) -> List[Annotation]:
        """
        Returns all annotations for a given annotation set

        Args:
            dataset_id: dataset id
            annotation_set_id: annotation set id

        Returns:
             List[:class:`remo.Annotation`]
        """
        images = self.list_dataset_images(dataset_id)
        annotations = []
        for img in images:
            annotations += self.list_image_annotations(dataset_id, annotation_set_id, img.id)
        return annotations

    def create_annotation_set(
        self, annotation_task: str, dataset_id: int, name: str, classes: List[str] = []
    ) -> AnnotationSet:
        """
        Creates a new annotation set within the given dataset

        Args:
            annotation_task: specified task for the annotation set. See also: :class:`remo.task`
            dataset_id: dataset id
            name: name of the annotation set
            classes: list of classes. Default is no classes

        Returns:
            :class:`remo.AnnotationSet`
        """
        annotation_set = self.api.create_annotation_set(annotation_task, dataset_id, name, classes)
        if 'error' in annotation_set:
            raise Exception(
                'Error while creating an annotation set. Message:\n{}'.format(annotation_set['error'])
            )

        return AnnotationSet(
            id=annotation_set['id'],
            name=annotation_set['name'],
            task=annotation_set['task'],
            dataset_id=annotation_set['dataset_id'],
            total_classes=len(annotation_set['classes']),
        )

    def add_annotations_to_image(self, annotation_set_id: int, image_id: int, annotations: List[Annotation]):
        """
        Adds annotation to a given image
        #TODO: check instance segmentation
        
        Args:
            annotation_set_id: annotation set id
            image_id: image id
            annotations: Annotation object
        """
        annotation_set = self.get_annotation_set(annotation_set_id)
        dataset_id = annotation_set.dataset_id

        annotation_info = self.get_annotation_info(dataset_id, annotation_set_id, image_id)
        object_id = len(annotation_info)

        objects = []
        classes = []

        for item in annotations:
            if item.bbox:
                objects.append(
                    {
                        "name": "OBJ " + str(object_id),
                        "coordinates": [
                            {"x": item.bbox.xmin, "y": item.bbox.ymin},
                            {"x": item.bbox.xmax, "y": item.bbox.ymax},
                        ],
                        "auto_created": False,
                        "position_number": object_id,
                        "classes": [
                            {"name": cls, "lower": cls.lower(), "questionable": False} for cls in item.classes
                        ],
                        "objectId": object_id,
                        "isHidden": False,
                    }
                )
                object_id += 1

            elif item.segment:
                objects.append(
                    {
                        "name": "OBJ " + str(object_id),
                        "coordinates": item.segment.points,
                        "auto_created": False,
                        "position_number": object_id,
                        "classes": [
                            {"name": cls, "lower": cls.lower(), "questionable": False} for cls in item.classes
                        ],
                        "objectId": object_id,
                        "isHidden": False,
                    }
                )
                object_id += 1
            else:
                classes += [
                    {"name": cls, "lower": cls.lower(), "questionable": False} for cls in item.classes
                ]

        return self.api.add_annotation(
            dataset_id, annotation_set_id, image_id, annotation_info, classes=classes, objects=objects
        )

    def list_annotation_set_classes(self, annotation_set_id: int) -> List[str]:
        """
        List classes within the annotation set

        Args:
            annotation_set_id: annotation set id

        Returns:
            list of classes
        """
        classes_with_ids = self.api.list_annotation_set_classes(annotation_set_id)
        return [item.get('name') for item in classes_with_ids]

    def list_dataset_images(self, dataset_id: int, limit: int = None, offset: int = None) -> List[Image]:
        """
        Returns a list of images within a dataset with given dataset_id

        Args:
            dataset_id: dataset id
            limit: limits result images
            offset: specifies offset
        Returns:
             List[:class:`remo.Image`]
        """
        json_data = self.api.list_dataset_images(dataset_id, limit=limit, offset=offset)
        if 'error' in json_data:
            raise Exception(
                'Failed to get all images for dataset ID = {}. Error message:\n: {}'.format(
                    dataset_id, json_data.get('error')
                )
            )

        images = json_data.get('results', [])
        return [Image(**img) for img in images]

    def get_image_content(self, url: str) -> bytes:
        """
        Get image file content by url

        Args:
            url: image url

        Returns:
            image binary data
        """
        return self.api.get_image_content(url)

    def get_image(self, image_id: int) -> Image:
        """
        Retrieves image by a given image id

        Args:
            image_id: image id

        Returns:
            :class:`remo.Image`
        """
        json_data = self.api.get_image(image_id)
        if 'error' in json_data:
            raise Exception(
                'Failed to get image by ID = {}. Error message:\n: {}'.format(
                    image_id, json_data.get('error')
                )
            )

        return Image(**json_data)

    def search_images(
        self, classes=None, task: str = None, dataset_id: int = None, limit: int = None,
    ):
        """
        Search images by class and annotation task

        Args:
            classes: string or list of strings - search for images which match all given classes
            task: name of the annotation task to filter dataset
            dataset_id: narrows search result to given dataset
            limit: limits number of search results

        Returns:
            image_id, dataset_id, name, annotations
        """
        # TODO: check this function
        return self.api.search_images(classes, task, dataset_id, limit)

    def view_search(self):
        """
        Opens browser in search page
        """
        return self._view(frontend.search)

    def view_image(self, image_id: int, dataset_id: int):
        """
        Opens browser on the image view for given image

        Args:
            image_id: image id
            dataset_id: dataset id
        """
        img = self.get_image(image_id)
        if not img:
            return

        if img.dataset_id != dataset_id:
            raise Exception('Image ID = {} not found in dataset ID: {}'.format(image_id, dataset_id))

        return self._view(frontend.image_view.format(image_id, dataset_id))

    def open_ui(self):
        """
        Opens the main page of Remo
        """
        return self._view(frontend.datasets)

    def view_dataset(self, id: int):
        """
        Opens browser for the given dataset

        Args:
            id: dataset id
        """
        return self._view(frontend.datasets, id)

    def view_annotation_tool(self, id: int):
        """
        Opens browser in annotation view for the given annotation set

        Args:
            id: annotation set id
        """
        return self._view(frontend.annotation.format(id))

    def view_annotate_image(self, annotation_set_id: int, image_id: int):
        """
        Opens browser on the annotation tool for giving image

        Args:
            annotation_set_id: annotation set id
            image_id: image id
        """
        return self._view(frontend.annotate_image.format(annotation_set_id, image_id))

    def view_annotation_stats(self, annotation_set_id: int):
        """
        Opens browser in annotation set insights page

        Args:
            annotation_set_id: annotation set id
        """
        return self._view(frontend.annotation_set_insights.format(annotation_set_id))

    def _view(self, url, *args, **kwargs):
        return self.viewer.browse(self.api.public_url(url, *args, **kwargs))
    
    def generate_annotations_from_folders(self, path_to_data_folder: str):
        """
        Creates a CSV annotation file for image classification tasks, where images are stored in folders with names matching the labels of the images. The CSV file is saved in the same input directory where images are stored. 
        Example of data structure for a dog / cat dataset: 
              - cats_and_dogs
                  - dog
                     - img1.jpg
                     - img2.jpg
                     - ...
                  - cat
                     - img199.jpg
                     - img200.jpg
                     - ...
            
        Example::
            # Download and unzip this sample dataset: s-3.s3-eu-west-1.amazonaws.com/cats_and_dogs.zip
            data_path = "cats_and_dogs"
            remo.generate_annotations_from_folders(path_to_data_folder=data_path)
            
        Args: 
               path_to_data_folder: path to the source folder where data is stored

        Returns: 
                csv_annotation_path: string, path to the generated CSV annotation file
        """
        
        classes = [d.name for d in os.scandir(path_to_data_folder) if d.is_dir()]
        im_dict = {}
        for class_name in classes:
            im_list = os.listdir(os.path.join(path_to_data_folder, class_name))
            for im in im_list:
                im_dict[im] = class_name

        csv_annotation_path = os.path.join(path_to_data_folder, "annotations.csv")
        with open(csv_annotation_path, 'w', newline='') as csvfile:
            fieldnames = ["file_name", "class_name"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for key in im_dict:
                writer.writerow({'file_name': key, 'class_name': im_dict[key]})
        
        return csv_annotation_path  
