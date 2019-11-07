import os
import subprocess
import time
from pathlib import Path

import requests

from .utils import browse
from .config import parse_config
from .sdk import SDK
from .api import API
from .ui import UI
from .domain.task import AnnotationTask

REMO_HOME = os.getenv('REMO_HOME', str(Path.home().joinpath('.remo')))
cfg_path = str(os.path.join(REMO_HOME, 'remo.json'))
config = parse_config(cfg_path)

logs = None
server = None

if config:

    def launch_server(open_browser=True):
        server_url = '{}:{}'.format(config.server, config.port)
        version_endpoint = '{}/version'.format(server_url)
        try:
            resp = requests.get(version_endpoint)
            print('Remo server is running:', resp.json())
            if open_browser:
                browse('{}:{}'.format(config.server, config.port))

            return True
        except:
            pass

        print('Launching Remo server ...')

        if not os.path.exists(config.conda_env):
            print("""
WARNING: Provided conda environment does not exist at {}

Failed to launch Remo server, please start it manually.

To fix config issue, please run init or update for Remo server (inside Remo conda env), like: 
python -m remo_app init
or
python -m remo_app update
""".format(config.conda_env))
            return False

        global logs
        global server
        logs = open(str(os.path.join(REMO_HOME, 'logs.txt')), 'w')

        path_args = ['python'] if os.name == 'nt' else ['bin', 'python']
        python_exe = os.path.join(config.conda_env, *path_args)

        server = subprocess.Popen(
            '{} -m remo_app'.format(python_exe),
            stdout=logs, stderr=logs,
            shell=True, universal_newlines=True,
        )

        time.sleep(5)
        retry = 5
        while retry > 0:
            print('Checking if server up ... ', retry)
            try:
                resp = requests.get(version_endpoint)
                print('Remo server is running:', resp.json())
                if open_browser:
                    browse(server_url)

                return True
            except:
                time.sleep(1)
            retry -= 1

        print('Failed to launch Remo server, please start it manually')
        return False


    launch_server(open_browser=False)

    server_url = '{}:{}'.format(config.server, config.port)
    api = API(server_url, config.user_email, config.user_password)
    ui = UI(server_url)
    sdk = SDK(api, ui)

    list_datasets = sdk.list_datasets
    get_dataset = sdk.get_dataset
    view_search = sdk.view_search
    create_dataset = sdk.create_dataset
    export_annotation_to_csv = sdk.export_annotation_to_csv
    search_images = sdk.search_images
    annotation_statistics = sdk.annotation_statistics
    list_annotation_sets = sdk.list_annotation_sets
    add_data_to_dataset = sdk.add_data_to_dataset
    view_image = sdk.view_image

    def terminate_server():
        global logs
        global server
        print('Terminating Remo server')
        if server:
            server.terminate()
            logs.close()

else:
    print("""
    WARNING: Config not found in {}
    
    Please run init or update for Remo server (inside Remo conda env), like: 
    
    python -m remo_app init
    or
    python -m remo_app update
    
    """.format(cfg_path))
