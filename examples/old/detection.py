import pandas as pd
import cv2
import os
from darkflow.net.build import TFNet
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def convert_row(image_path, annotation_path, row):
    vals = ('train', row['file_name'], image_path + row['file_name'], str(row['width']), str(row['height']),)

    for i in range(len(row['class'])):
        vals = vals + (row['class'][i].lower(), str(row['xmin'][i]), str(row['ymin'][i]),
                       str(row['xmax'][i]), str(row['ymax'][i]),)

    result = """<annotation>
    <folder>%s</folder>
    <filename>%s</filename>
    <path>%s</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>%s</width>
        <height>%s</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    """ + """<object>
        <name>%s</name>
        <pose>Unspecified</pose>
        <truncated>0</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>%s</xmin>
            <ymin>%s</ymin>
            <xmax>%s</xmax>
            <ymax>%s</ymax>
        </bndbox>
    </object>""" * len(row['class']) + """
</annotation>
"""
    result = result % vals
    filename = row['file_name'].split('.')[0]
    path = annotation_path + filename
    f = open(path + ".xml", "w")
    f.write(result)
    f.close()

def prepare_data(path_to_csv_annotations, image_path, annotation_path):

    df = pd.read_csv(path_to_csv_annotations)
    df_grouped = df.groupby('file_name')['class'].apply(list).reset_index(name='class')
    for column in df.columns[2:]:
        df_new = df.groupby('file_name')[column].apply(list).reset_index(name=column)
        df_grouped = df_grouped.merge(df_new, on=['file_name'])
    # height and width is the same
    df_grouped['height'] = df_grouped['height'].apply(lambda x: x[0])
    df_grouped['width'] = df_grouped['width'].apply(lambda x: x[0])
    df_grouped.apply(lambda x: convert_row(image_path, annotation_path, x), axis=1)

def train_yolo(model_cfg, weights, batch_size, epoch, annotation_path, image_path, label_path, backup_path):
    options = {"model": model_cfg ,
               "load": weights,
               "batch": batch_size,
               "epoch": epoch,
               "train": True,
               "verbalise": False,
               "annotation": annotation_path,
               "dataset": image_path,
               "labels": label_path,
               "backup": backup_path}
    tfnet = TFNet(options)
    tfnet.train()

def test_yolo(model_cfg, load, threshold, label_path, backup_path):
    options = {
        "model": model_cfg ,
        "load": load,
        'threshold': threshold,
        "verbalise": False,
        "labels": label_path,
        "backup": backup_path}

    tfnet2 = TFNet(options)
    tfnet2.load_from_ckpt()
    return tfnet2

def predict_yolo(model_cfg, load, threshold, label_path, backup_path, root_path, classes):
    tfnet2 = test_yolo(model_cfg, load, threshold, label_path, backup_path)
    for cls in classes:
        class_to_predict_files = os.listdir(root_path+cls)
        results = []
        for img_file in class_to_predict_files:
            cls_pth = root_path + cls
            img_path = os.path.join(cls_pth, img_file)
            original_img = cv2.imread(img_path)
            original_img = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
            outputs = tfnet2.return_predict(original_img)
            result = {'file_name':img_file, 'objects':outputs}
            results.append(result)
    return results

def post_process(results):
    df = pd.DataFrame(columns=['file_name','class','xmin','ymin','xmax','ymax'])
    for res in results:
        for i in range(len(res['objects'])):
            df.loc[len(df)+1] = [res['file_name'], d.get(res['objects'][i]['label']).capitalize(),res['objects'][i]['topleft']['x'],res['objects'][i]['topleft']['y'], res['objects'][i]['bottomright']['x'], res['objects'][i]['bottomright']['y']]
    # drop the other classes different than car and person.
    df = df.dropna(subset=['class'])
    return df