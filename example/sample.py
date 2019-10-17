import time

import remo

if __name__ == '__main__':
    print('Hello')
    # sdk = remo.SDK('https://stage.remo.ai', 'admin@remo.ai', 'Wash&g0')
    sdk = remo.SDK('http://localhost:8000', 'admin@remo.ai', 'adminpass')

    dataset = sdk.create_dataset('Demo: local files', local_files=['/Users/vovka/Downloads/Datasets/COCO/2014'])
    print('dataset:', dataset)

    # dataset.upload(urls=["https://remo-sample-datasets.s3-eu-west-1.amazonaws.com/Imagenet_sample_dataset.zip"],
    #                annotation_task=remo.AnnotationTask.image_classification)
    # dataset.browse()
    #
    # # wait a bit for uploading and parsing annotations
    # time.sleep(5)
    # dataset.fetch()
    # dataset.annotate()
