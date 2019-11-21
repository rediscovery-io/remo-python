from .domain.annotation_set import AnnotationSet
from .domain.dataset import Dataset, Image
from .domain import task
from .sdk import SDK

_logs = None
_server = None


def __init__():
    import os
    from pathlib import Path
    from .config import parse_config

    REMO_HOME = os.getenv('REMO_HOME', str(Path.home().joinpath('.remo')))
    cfg_path = str(os.path.join(REMO_HOME, 'remo.json'))
    config = parse_config(cfg_path)

    if config:
        if config.viewer == 'electron':
            from .electron import browse
        else:
            from .browser import browse

        server_url = '{}:{}'.format(config.server, config.port)

        def terminate_server():
            global _logs
            global _server
            print('Terminating Remo server')
            if _server:
                _server.terminate()
                _logs.close()

        def launch_server(open_browser=True):
            import time
            import requests


            version_endpoint = '{}/version'.format(server_url)
            try:
                resp = requests.get(version_endpoint)
                print("""
    (\(\ 
    (>':') Remo server is running: {}
                """.format(resp.json()))
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

            global _logs
            global _server
            _logs = open(str(os.path.join(REMO_HOME, 'logs.txt')), 'w')

            path_args = ['python'] if os.name == 'nt' else ['bin', 'python']
            python_exe = os.path.join(config.conda_env, *path_args)

            import subprocess
            _server = subprocess.Popen(
                '{} -m remo_app'.format(python_exe),
                stdout=_logs, stderr=_logs,
                shell=True, universal_newlines=True,
            )

            time.sleep(5)
            retry = 5
            while retry > 0:
                print('Wait a bit... ', retry)
                try:
                    resp = requests.get(version_endpoint)
                    print("""
    (\(\ 
    (>':') Remo server is running: {}
                    """.format(resp.json()))
                    if open_browser:
                        browse(server_url)

                    return True
                except:
                    time.sleep(1)
                retry -= 1

            print('Failed to launch Remo server, please start it manually')
            return False

        launch_server(open_browser=False)

        sdk = SDK(server_url, config.user_email, config.user_password, browse)

        # set access to public SDK methods
        import sys
        is_public_sdk_method = lambda name: not name.startswith('_') and callable(getattr(sdk, name))
        functions = filter(is_public_sdk_method, dir(sdk))
        for name in functions:
            setattr(sys.modules[__name__], name, getattr(sdk, name))

        setattr(sys.modules[__name__], 'launch_server', launch_server)
        setattr(sys.modules[__name__], 'terminate_server', terminate_server)

    else:
        print("""
        WARNING: Config not found in {}
        
        Please run init or update for Remo server (inside Remo conda env), like: 
        
        python -m remo_app init
        or
        python -m remo_app update
        
        """.format(cfg_path))


__init__()
