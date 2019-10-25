import os
import subprocess
import time
from pathlib import Path

import requests

from .config import parse_config
from .sdk import SDK
from .domain.task import AnnotationTask

REMO_HOME = os.getenv('REMO_HOME', str(Path.home().joinpath('.remo')))
cfg_path = str(os.path.join(REMO_HOME, 'remo.json'))
config = parse_config(cfg_path)

logs = None
server = None

if config:
    try:
        resp = requests.get('{}:{}/version'.format(config.server, config.port))
        print('Remo server is running:', resp.json())
    except:
        print('Launching Remo server ...')


        def launch_server():
            global logs
            global server
            logs = open(str(os.path.join(REMO_HOME, 'logs.txt')), 'w')

            python_exe = os.path.join(config.conda_env, 'bin', 'python')

            server = subprocess.Popen(
                '{} -m rediscovery'.format(python_exe),
                stdout=logs, stderr=logs,
                shell=True, universal_newlines=True,
            )

            time.sleep(5)
            retry = 5
            while retry > 0:
                print('Checking if server up ... ', retry)
                try:
                    resp = requests.get('{}:{}/version'.format(config.server, config.port))
                    print('Remo server is running:', resp.json())
                    break
                except:
                    time.sleep(1)
                retry -= 1
                if retry == 0:
                    print('Failed to launch Remo server, please start it manually')

        launch_server()

    sdk = SDK('{}:{}'.format(config.server, config.port), config.user_email, config.user_password)

    login = sdk.login
    list_datasets = sdk.list_datasets
    get_dataset = sdk.get_dataset
    search_images = sdk.search_images
    create_dataset = sdk.create_dataset

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
    
    python -m rediscovery init
    or
    python -m rediscovery update
    
    """.format(cfg_path))


