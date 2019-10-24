import os
from pathlib import Path

from .config import parse_config
from .sdk import SDK
from .domain.task import AnnotationTask

REMO_HOME = os.getenv('REMO_HOME', str(Path.home().joinpath('.remo')))
cfg_path = str(os.path.join(REMO_HOME, 'config.json'))
config = parse_config(cfg_path)

if config:
    sdk = SDK('http://localhost:{}'.format(config.port), config.user_email, config.user_password)

    login = sdk.login
    list_datasets = sdk.list_datasets
    get_dataset = sdk.get_dataset
    search_images = sdk.search_images
    create_dataset = sdk.create_dataset
    get_annotation_set = sdk.get_annotation_set

else:
    print('WARNING: Config not found')


