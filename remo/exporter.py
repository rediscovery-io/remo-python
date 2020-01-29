from .domain import task


def get_json_to_csv_exporter(annotation_task):
    return json_to_csv_exporters.get(annotation_task)


def export_object_detection_json_to_csv(annotation_results, csv_writer):
    header = ['file_name', 'class', 'xmin', 'ymin', 'xmax', 'ymax', 'height', 'width']
    csv_writer.writerow(header)
    for img in annotation_results:
        file_name = img['file_name']
        objects = img['annotations']

        for obj in objects:
            classes = obj['classes']
            bbox = list(obj['bbox'].values())
            for cls in classes:
                csv_writer.writerow([file_name, cls] + bbox + [img['height'], img['width']])


def export_instance_segmentation_json_to_csv(annotation_results, csv_writer):
    header = ['file_name', 'class', 'coordinates']
    csv_writer.writerow(header)

    for img in annotation_results:
        file_name = img['file_name']
        objects = img['annotations']

        for obj in objects:
            classes = obj['classes']
            segments = obj['segments']
            values = [v for s in segments for v in s.values()]
            coordinates = ' '.join(map(str, values))
            for cls in classes:
                csv_writer.writerow([file_name, cls, coordinates])


def export_image_classification_json_to_csv(annotation_results, csv_writer):
    header = ['file_name', 'class']
    csv_writer.writerow(header)

    for img in annotation_results:
        file_name = img['file_name']
        classes = img['classes']

        for cls in classes:
            csv_writer.writerow([file_name, cls])


json_to_csv_exporters = {
    task.object_detection: export_object_detection_json_to_csv,
    task.instance_segmentation: export_instance_segmentation_json_to_csv,
    task.image_classification: export_image_classification_json_to_csv
}
