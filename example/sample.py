import time

import remo

if __name__ == '__main__':
    sdk = remo.SDK('https://stage.remo.ai', 'admin@remo.ai', 'Wash&g0')

    dataset = sdk.create_dataset('Demo: imagenet')
    dataset.upload(urls=["https://remo-sample-datasets.s3-eu-west-1.amazonaws.com/Imagenet_sample_dataset.zip"],
                   annotation_task=remo.AnnotationTask.image_classification)
    dataset.browse()

    # wait a bit for uploading and parsing annotations
    time.sleep(5)
    dataset.fetch()
    dataset.annotate()
